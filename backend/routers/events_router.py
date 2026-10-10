import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import (
    Event, EventRequirement, EventService, Service, EventCategory,
    EventType, User, AuditLog, EventPackage
)
from backend.schemas import EventCreateRequest, EventUpdateRequest, EventOut
from backend.auth import get_current_user

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.post("", response_model=EventOut)
def create_event(
    req: EventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cat = db.query(EventCategory).filter(EventCategory.id == req.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Selected event category does not exist.")

    # Create event record
    event = Event(
        user_id=current_user.id,
        category_id=req.category_id,
        event_type_id=req.event_type_id,
        title=req.title,
        event_date=req.event_date,
        start_time=req.start_time,
        end_time=req.end_time,
        expected_attendees=req.expected_attendees,
        budget=req.budget,
        venue_type=req.venue_type,
        preferred_locality=req.preferred_locality,
        venue_address=req.venue_address,
        indoor_outdoor=req.indoor_outdoor,
        theme=req.theme,
        status="draft",
        is_custom=req.is_custom or False
    )
    db.add(event)
    db.flush()

    # Create Dynamic Requirements
    requirement = EventRequirement(
        event_id=event.id,
        form_data_json=json.dumps(req.form_data or {}),
        special_instructions=req.special_instructions,
        tradition_notes=req.tradition_notes,
        dietary_preferences=req.dietary_preferences or "mixed",
        av_requirements=req.av_requirements,
        stage_requirements=req.stage_requirements,
        accessibility_notes=req.accessibility_notes
    )
    db.add(requirement)

    # Attach selected services or package services
    services_to_add = {}
    if req.package_id:
        pkg = db.query(EventPackage).filter(EventPackage.id == req.package_id).first()
        if pkg:
            for ps in pkg.package_services:
                services_to_add[ps.service_id] = ps.included_quantity
                
    if req.services:
        for s in req.services:
            services_to_add[s.service_id] = s.quantity

    for svc_id, qty in services_to_add.items():
        svc = db.query(Service).filter(Service.id == svc_id).first()
        if svc:
            es = EventService(
                event_id=event.id,
                service_id=svc.id,
                quantity=qty,
                unit_price=svc.base_price,
                total_price=svc.base_price * qty,
                is_selected=True
            )
            db.add(es)

    audit = AuditLog(
        user_id=current_user.id,
        action="EVENT_CREATED",
        entity_type="event",
        entity_id=event.id
    )
    db.add(audit)
    db.commit()
    db.refresh(event)

    return _format_event_out(event)

@router.get("", response_model=List[EventOut])
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Customer record isolation:
    # Customers only see their own events. Admins can see all events.
    if current_user.role == "admin":
        events = db.query(Event).order_by(Event.created_at.desc()).all()
    else:
        events = db.query(Event).filter(Event.user_id == current_user.id).order_by(Event.created_at.desc()).all()
        
    return [_format_event_out(e) for e in events]

@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    # Customer record isolation check
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this event record.")

    return _format_event_out(event)

@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    req: EventUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to update this event.")

    if req.title:
        event.title = req.title
    if req.event_date:
        event.event_date = req.event_date
    if req.expected_attendees is not None:
        event.expected_attendees = req.expected_attendees
    if req.budget is not None:
        event.budget = req.budget
    if req.venue_type:
        event.venue_type = req.venue_type
    if req.preferred_locality:
        event.preferred_locality = req.preferred_locality

    if req.form_data is not None and event.requirement:
        event.requirement.form_data_json = json.dumps(req.form_data)

    if req.services is not None:
        # Clear existing services and attach updated
        db.query(EventService).filter(EventService.event_id == event.id).delete()
        for s in req.services:
            svc = db.query(Service).filter(Service.id == s.service_id).first()
            if svc:
                es = EventService(
                    event_id=event.id,
                    service_id=svc.id,
                    quantity=s.quantity,
                    unit_price=svc.base_price,
                    total_price=svc.base_price * s.quantity,
                    notes=s.notes,
                    is_selected=True
                )
                db.add(es)

    audit = AuditLog(
        user_id=current_user.id,
        action="EVENT_UPDATED",
        entity_type="event",
        entity_id=event.id
    )
    db.add(audit)
    db.commit()
    db.refresh(event)

    return _format_event_out(event)

def _format_event_out(event: Event) -> EventOut:
    form_data = {}
    if event.requirement and event.requirement.form_data_json:
        try:
            form_data = json.loads(event.requirement.form_data_json)
        except Exception:
            pass
            
    return EventOut(
        id=event.id,
        user_id=event.user_id,
        category_id=event.category_id,
        category_name=event.category.name if event.category else "",
        category_code=event.category.code if event.category else "",
        event_type_id=event.event_type_id,
        event_type_name=event.event_type.name if event.event_type else None,
        title=event.title,
        event_date=event.event_date,
        start_time=event.start_time,
        end_time=event.end_time,
        expected_attendees=event.expected_attendees,
        budget=event.budget,
        venue_type=event.venue_type,
        preferred_locality=event.preferred_locality,
        venue_address=event.venue_address,
        indoor_outdoor=event.indoor_outdoor,
        theme=event.theme,
        status=event.status,
        is_custom=event.is_custom,
        created_at=event.created_at,
        form_data=form_data,
        special_instructions=event.requirement.special_instructions if event.requirement else None,
        tradition_notes=event.requirement.tradition_notes if event.requirement else None,
        dietary_preferences=event.requirement.dietary_preferences if event.requirement else None
    )
