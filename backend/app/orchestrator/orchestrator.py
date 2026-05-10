from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.ticket import Ticket, InputEvent
from app.models.report import Report
from app.models.customer import Customer
from app.models.department import Department
from app.models.user import User  # noqa: imported for SQLAlchemy mapper
from app.orchestrator.routing_matrix import get_target_departments

# Import specific agents
from app.agents.surveillance_risque_credit import SurveillanceRisqueCreditAgent
from app.agents.analyse_credit_ggei import AnalyseCreditGGEIAgent
from app.agents.donnees_analytiques import DonneesAnalytiquesAgent
from app.agents.regionale_sfax import RegionaleSfaxAgent
from app.agents.controle_gestion_alm import ControleGestionALMAgent
from app.agents.garanties import GarantiesAgent
from app.agents.base import BaseAgent
from app.api.v1.stream import broadcast_event_sync
from app.core.audit import log_event

import time

# Map department IDs to specific agent classes
AGENT_MAPPING = {
    "DIR_RISQUE": SurveillanceRisqueCreditAgent,
    "DIR_GGEI": AnalyseCreditGGEIAgent,
    "DIR_DATA": DonneesAnalytiquesAgent,
    "DIR_SFAX": RegionaleSfaxAgent,
    "DIR_ALM": ControleGestionALMAgent,
    "DIR_GARANTIES": GarantiesAgent,
}


def _get_or_create_agent(dept_id: str, db: Session) -> BaseAgent:
    agent_class = AGENT_MAPPING.get(dept_id)
    if not agent_class:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        dept_name = dept.name if dept else dept_id
        return BaseAgent(department_id=dept_id, department_name=dept_name, role_description="Provide risk analysis.")
    return agent_class()


def process_new_event(db: Session, payload: Dict[str, Any], ticket_id: Optional[int] = None) -> Ticket:
    """
    Main orchestration flow. Called from the background thread in inputs.py.
    ticket_id is passed in if the ticket was already created by the route handler.
    """
    customer_id = payload.get("customer_id")
    event_type = payload.get("event_type", "early_warning")
    details = payload.get("details", "")

    # Get or reuse ticket
    if ticket_id:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    else:
        ticket = Ticket(customer_id=customer_id, status="open")
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        input_event = InputEvent(ticket_id=ticket.id, source="api", payload=payload)
        db.add(input_event)
        db.commit()

        log_event(db, "ticket_created", "ticket", ticket.id, details={
            "customer_id": customer_id,
            "event_type": event_type,
            "ticket_id": ticket.id,
        })
        broadcast_event_sync("ticket_created", {"ticket_id": ticket.id, "customer_id": customer_id})

    # Get customer data for routing
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    customer_data = {"segment": "Unknown", "loan_size": 0, "risk_stage": 1}
    if customer:
        customer_data = {
            "segment": customer.segment,
            "loan_size": customer.loan_size,
            "risk_stage": customer.risk_stage,
        }

    # Routing Matrix
    target_depts = get_target_departments(
        event_type=event_type,
        customer_segment=customer_data["segment"],
        loan_size=customer_data["loan_size"],
    )

    log_event(db, "routing_complete", "ticket", ticket.id, details={
        "ticket_id": ticket.id,
        "target_depts": target_depts,
        "event_type": event_type,
    })

    broadcast_event_sync("routing_complete", {
        "ticket_id": ticket.id,
        "target_depts": target_depts,
    })

    # Run each department agent sequentially
    for dept_id in target_depts:
        agent = _get_or_create_agent(dept_id, db)

        log_event(db, "agent_started", "ticket", ticket.id, details={
            "ticket_id": ticket.id,
            "dept_id": dept_id,
        })
        broadcast_event_sync("agent_started", {
            "ticket_id": ticket.id,
            "dept_id": dept_id,
        })

        ticket_data = {"id": ticket.id}
        analysis_result = agent.analyze(ticket_data, customer_data, details)

        # Save report
        report = Report(
            ticket_id=ticket.id,
            department_id=dept_id,
            content=analysis_result,
            status="pending",
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        log_event(db, "agent_done", "report", report.id, details={
            "ticket_id": ticket.id,
            "dept_id": dept_id,
            "report_id": report.id,
            "content": analysis_result,
        })
        broadcast_event_sync("agent_done", {
            "ticket_id": ticket.id,
            "dept_id": dept_id,
            "report_id": report.id,
            "content": analysis_result,
        })

        # Small delay so frontend can animate each card arriving
        time.sleep(0.3)

    # Mark ticket as analysis_complete
    ticket.status = "analysis_complete"
    db.commit()

    broadcast_event_sync("analysis_complete", {
        "ticket_id": ticket.id,
        "total_reports": len(target_depts),
    })

    return ticket


def reanalyze_report(report_id: int):
    """
    Re-run the LLM for a specific report (called after invalidation).
    Creates its own DB session.
    """
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return

        ticket = db.query(Ticket).filter(Ticket.id == report.ticket_id).first()
        if not ticket:
            return

        # Get original event details
        input_event = db.query(InputEvent).filter(InputEvent.ticket_id == ticket.id).first()
        if not input_event:
            return

        payload = input_event.payload
        customer = db.query(Customer).filter(Customer.id == ticket.customer_id).first()
        customer_data = {"segment": "Unknown", "loan_size": 0, "risk_stage": 1}
        if customer:
            customer_data = {
                "segment": customer.segment,
                "loan_size": customer.loan_size,
                "risk_stage": customer.risk_stage,
            }

        broadcast_event_sync("agent_started", {
            "ticket_id": ticket.id,
            "dept_id": report.department_id,
            "reanalysis": True,
        })

        agent = _get_or_create_agent(report.department_id, db)
        ticket_data = {"id": ticket.id}
        new_content = agent.analyze(ticket_data, customer_data, payload.get("details", ""))

        report.content = new_content
        report.status = "pending"
        db.commit()
        db.refresh(report)

        log_event(db, "agent_reanalysis_done", "report", report.id, details={
            "ticket_id": ticket.id,
            "dept_id": report.department_id,
            "report_id": report.id,
            "content": new_content,
        })

        broadcast_event_sync("agent_done", {
            "ticket_id": ticket.id,
            "dept_id": report.department_id,
            "report_id": report.id,
            "content": new_content,
            "reanalysis": True,
        })

    except Exception as e:
        print(f"[Reanalysis Error] Report {report_id}: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()
