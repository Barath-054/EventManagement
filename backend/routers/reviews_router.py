from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Review, Event, User, AuditLog
from backend.schemas import ReviewCreate, ReviewOut
from backend.auth import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["Post-Event Reviews & Feedback"])

@router.post("", response_model=ReviewOut)
def submit_review(
    req: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to submit review for this event.")

    rev = Review(
        event_id=event.id,
        user_id=current_user.id,
        rating=req.rating,
        title=req.title,
        feedback_text=req.feedback_text
    )
    db.add(rev)
    
    # Mark event as completed if not already
    event.status = "completed"
    
    audit = AuditLog(
        user_id=current_user.id,
        action="REVIEW_SUBMITTED",
        entity_type="review",
        entity_id=event.id
    )
    db.add(audit)
    db.commit()
    db.refresh(rev)

    return ReviewOut(
        id=rev.id,
        event_id=rev.event_id,
        user_name=current_user.full_name,
        rating=rev.rating,
        title=rev.title,
        feedback_text=rev.feedback_text,
        created_at=rev.created_at
    )

@router.get("", response_model=List[ReviewOut])
def get_reviews(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    results = []
    for r in reviews:
        results.append(ReviewOut(
            id=r.id,
            event_id=r.event_id,
            user_name=r.user.full_name if r.user else "Anonymous Client",
            rating=r.rating,
            title=r.title,
            feedback_text=r.feedback_text,
            created_at=r.created_at
        ))
    return results
