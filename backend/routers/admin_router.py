from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from backend.database import get_db
from backend.models import (
    Event, EventCategory, Booking, Quotation, Payment,
    User, Service, EventService, Review, Vendor, Venue
)
from backend.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])

@router.get("/metrics")
def get_admin_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total_events = db.query(Event).count()
    total_bookings = db.query(Booking).count()
    pending_quotes = db.query(Quotation).filter(Quotation.status == "pending").count()
    approved_quotes = db.query(Quotation).filter(Quotation.status == "approved").count()
    
    # Financial sums
    total_revenue_collected = db.query(func.sum(Payment.amount)).filter(Payment.status == "completed").scalar() or 0.0
    total_balance_due = db.query(func.sum(Booking.balance_due)).scalar() or 0.0
    
    # Events grouped by category
    cat_counts = (
        db.query(EventCategory.name, func.count(Event.id))
        .join(Event, EventCategory.id == Event.category_id, isouter=True)
        .group_by(EventCategory.name)
        .all()
    )
    events_by_category = [{"category": name, "count": count} for name, count in cat_counts if count > 0]
    
    # Events grouped by locality
    loc_counts = (
        db.query(Event.preferred_locality, func.count(Event.id))
        .group_by(Event.preferred_locality)
        .all()
    )
    events_by_locality = [{"locality": loc, "count": count} for loc, count in loc_counts if loc]
    
    # Recent Bookings
    recent_bookings = (
        db.query(Booking)
        .order_by(Booking.confirmed_at.desc())
        .limit(5)
        .all()
    )
    recent_bookings_data = []
    for b in recent_bookings:
        recent_bookings_data.append({
            "id": b.id,
            "reference": b.booking_reference,
            "event_title": b.event.title if b.event else "",
            "category": b.event.category.name if b.event and b.event.category else "",
            "status": b.status,
            "advance_paid": b.advance_paid,
            "confirmed_at": b.confirmed_at.strftime("%d-%m-%Y")
        })

    return {
        "total_events": total_events,
        "total_bookings": total_bookings,
        "pending_quotations": pending_quotes,
        "approved_quotations": approved_quotes,
        "total_revenue_collected": round(total_revenue_collected, 2),
        "total_balance_due": round(total_balance_due, 2),
        "events_by_category": events_by_category,
        "events_by_locality": events_by_locality,
        "recent_bookings": recent_bookings_data
    }

@router.get("/events")
def get_all_events_filtered(
    category_id: Optional[int] = None,
    locality: Optional[str] = None,
    status: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(Event)
    if category_id:
        query = query.filter(Event.category_id == category_id)
    if locality:
        query = query.filter(Event.preferred_locality == locality)
    if status:
        query = query.filter(Event.status == status)
    if min_budget is not None:
        query = query.filter(Event.budget >= min_budget)
    if max_budget is not None:
        query = query.filter(Event.budget <= max_budget)
        
    events = query.order_by(Event.created_at.desc()).all()
    
    results = []
    for e in events:
        results.append({
            "id": e.id,
            "title": e.title,
            "category_name": e.category.name if e.category else "",
            "user_name": e.user.full_name if e.user else "",
            "user_email": e.user.email if e.user else "",
            "event_date": e.event_date,
            "attendees": e.expected_attendees,
            "budget": e.budget,
            "preferred_locality": e.preferred_locality,
            "venue_type": e.venue_type,
            "status": e.status,
            "created_at": e.created_at.strftime("%d-%m-%Y %H:%M")
        })
    return results
