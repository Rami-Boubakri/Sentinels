from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.report import Report
from app.models.action import Action
from app.schemas.common import ReportOut, ActionOut
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter()


class ValidateRequest(BaseModel):
    action_taken: str


class ModifyRequest(BaseModel):
    content: Dict[str, Any]


@router.get("/", response_model=List[ReportOut])
def list_reports(
    ticket_id: Optional[int] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Report)
    if ticket_id:
        query = query.filter(Report.ticket_id == ticket_id)
    if department_id:
        query = query.filter(Report.department_id == department_id)
    if status:
        query = query.filter(Report.status == status)
    return query.order_by(Report.id.desc()).all()


@router.get("/ticket/{ticket_id}", response_model=List[ReportOut])
def get_reports_for_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return db.query(Report).filter(Report.ticket_id == ticket_id).all()


@router.post("/{report_id}/validate", response_model=ActionOut)
def validate_report(report_id: int, request: ValidateRequest, db: Session = Depends(get_db)):
    from app.core.audit import log_event
    from app.api.v1.stream import get_event_loop, broadcast_event_sync

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = "validated"

    action = Action(
        report_id=report.id,
        department_id=report.department_id,
        action_taken=request.action_taken,
        status="executed",
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    # Audit log
    log_event(db, "report_validated", "report", report_id, details={
        "ticket_id": report.ticket_id,
        "dept_id": report.department_id,
        "action_taken": request.action_taken,
    })

    # SSE broadcast
    broadcast_event_sync("report_validated", {
        "ticket_id": report.ticket_id,
        "report_id": report_id,
        "dept_id": report.department_id,
        "action_taken": request.action_taken,
        "action_id": action.id,
    })

    return action


@router.post("/{report_id}/invalidate")
def invalidate_report(report_id: int, db: Session = Depends(get_db)):
    from app.core.audit import log_event
    from app.api.v1.stream import broadcast_event_sync
    from app.orchestrator.orchestrator import reanalyze_report

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = "invalidated"
    db.commit()

    log_event(db, "report_invalidated", "report", report_id, details={
        "ticket_id": report.ticket_id,
        "dept_id": report.department_id,
    })

    broadcast_event_sync("report_invalidated", {
        "ticket_id": report.ticket_id,
        "report_id": report_id,
        "dept_id": report.department_id,
    })

    # Trigger re-analysis in background
    import threading
    t = threading.Thread(target=reanalyze_report, args=(report_id,), daemon=True)
    t.start()

    return {"status": "invalidated", "report_id": report_id, "message": "Agent is rewriting the report."}


@router.patch("/{report_id}/modify")
def modify_report(report_id: int, request: ModifyRequest, db: Session = Depends(get_db)):
    from app.core.audit import log_event
    from app.api.v1.stream import broadcast_event_sync

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.content = request.content
    report.status = "modified"
    db.commit()

    log_event(db, "report_modified", "report", report_id, details={
        "ticket_id": report.ticket_id,
        "dept_id": report.department_id,
        "new_content": request.content,
    })

    broadcast_event_sync("report_modified", {
        "ticket_id": report.ticket_id,
        "report_id": report_id,
        "dept_id": report.department_id,
        "content": request.content,
    })

    return {"status": "modified", "report_id": report_id}
