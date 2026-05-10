from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.ticket import Ticket
from app.models.report import Report
from app.models.action import Action
from typing import Dict, Any

router = APIRouter()

@router.get("/unified")
def get_unified_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "open").count()
    total_actions = db.query(Action).count()
    
    # Get latest 10 reports
    latest_reports = db.query(Report).order_by(Report.id.desc()).limit(10).all()
    reports_data = [
        {
            "id": r.id,
            "department_id": r.department_id,
            "content": r.content,
            "status": r.status
        } for r in latest_reports
    ]
    
    return {
        "kpis": {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "total_actions": total_actions
        },
        "recent_reports": reports_data
    }

@router.get("/department/{department_id}")
def get_department_dashboard(department_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    pending_reports = db.query(Report).filter(
        Report.department_id == department_id,
        Report.status == "pending"
    ).count()
    
    executed_actions = db.query(Action).filter(
        Action.department_id == department_id
    ).count()
    
    return {
        "kpis": {
            "pending_reports": pending_reports,
            "executed_actions": executed_actions
        }
    }
