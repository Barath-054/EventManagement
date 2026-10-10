import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Booking, EventTask, Event, User, AuditLog
from backend.schemas import BookingOut, EventTaskOut
from backend.auth import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["Bookings & Event Execution"])

class TaskStatusUpdate(BaseModel):
    status: str  # pending, in_progress, completed

@router.get("/event/{event_id}", response_model=BookingOut)
def get_booking_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to booking for this event.")
        
    booking = db.query(Booking).filter(Booking.event_id == event_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="No booking confirmed yet for this event.")

    return _format_booking_out(booking)

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if current_user.role != "admin" and booking.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this booking.")

    return _format_booking_out(booking)

@router.put("/{booking_id}/tasks/{task_id}", response_model=EventTaskOut)
def update_task_status(
    booking_id: int,
    task_id: int,
    req: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if current_user.role != "admin" and booking.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to update task.")

    task = db.query(EventTask).filter(EventTask.id == task_id, EventTask.booking_id == booking_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in this booking.")

    task.status = req.status
    if req.status == "completed":
        task.completed_at = datetime.datetime.utcnow()
    else:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    return EventTaskOut(
        id=task.id,
        title=task.title,
        category=task.category,
        status=task.status,
        assigned_to=task.assigned_to,
        due_date=task.due_date,
        completed_at=task.completed_at
    )

def _format_booking_out(b: Booking) -> BookingOut:
    tasks = []
    for t in b.tasks:
        tasks.append(EventTaskOut(
            id=t.id,
            title=t.title,
            category=t.category,
            status=t.status,
            assigned_to=t.assigned_to,
            due_date=t.due_date,
            completed_at=t.completed_at
        ))
    return BookingOut(
        id=b.id,
        booking_reference=b.booking_reference,
        quotation_id=b.quotation_id,
        event_id=b.event_id,
        event_title=b.event.title if b.event else "",
        category_name=b.event.category.name if b.event and b.event.category else "",
        status=b.status,
        advance_paid=b.advance_paid,
        balance_due=b.balance_due,
        confirmed_at=b.confirmed_at,
        tasks=tasks
    )
