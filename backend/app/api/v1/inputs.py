from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.schemas.common import InputEventCreate
from app.security_layer.input_validator import validate_input_event
from app.orchestrator.orchestrator import process_new_event
from app.models.ticket import Ticket, InputEvent
from app.core.audit import log_event
from app.api.v1.stream import broadcast_event_sync
import threading

router = APIRouter()


def _run_pipeline(ticket_id: int, payload: dict):
    """
    Run the orchestrator pipeline in a background thread.
    Creates its own DB session so it doesn't share the request-scoped one.
    """
    db = SessionLocal()
    try:
        process_new_event(db, payload, ticket_id=ticket_id)
    except Exception as e:
        print(f"[Orchestrator Error] Ticket {ticket_id}: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


@router.post("/", status_code=202)
def submit_input_event(event: InputEventCreate, db: Session = Depends(get_db)):
    """
    Submit a new input event. Returns immediately with ticket_id so the
    frontend can redirect to the live ticket view while agents work.
    """
    is_valid, error_msg = validate_input_event(event.payload)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    payload = event.payload
    customer_id = payload.get("customer_id")

    # Create ticket synchronously so we can return ticket_id immediately
    ticket = Ticket(customer_id=customer_id, status="open")
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    input_ev = InputEvent(ticket_id=ticket.id, source=event.source, payload=payload)
    db.add(input_ev)
    db.commit()

    log_event(db, "ticket_created", "ticket", ticket.id, details={
        "customer_id": customer_id,
        "event_type": payload.get("event_type"),
        "ticket_id": ticket.id,
    })

    broadcast_event_sync("ticket_created", {
        "ticket_id": ticket.id,
        "customer_id": customer_id,
        "event_type": payload.get("event_type"),
    })

    # Run agents in background thread
    t = threading.Thread(
        target=_run_pipeline,
        args=(ticket.id, payload),
        daemon=True,
    )
    t.start()

    return {
        "status": "accepted",
        "ticket_id": ticket.id,
        "message": "Event is being processed. Agents are activating.",
    }
