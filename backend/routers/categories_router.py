from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import EventCategory, EventType, AuditLog, User
from backend.schemas import EventCategoryOut, EventCategoryCreate, EventTypeCreate, EventTypeOut
from backend.auth import require_admin, get_current_user

router = APIRouter(prefix="/api/categories", tags=["Event Categories"])

@router.get("", response_model=List[EventCategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(EventCategory).filter(EventCategory.is_active == True).order_by(EventCategory.display_order).all()
    return categories

@router.get("/{category_id}", response_model=EventCategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    return cat

@router.post("", response_model=EventCategoryOut)
def create_category(
    req: EventCategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    existing = db.query(EventCategory).filter(EventCategory.code == req.code.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this code already exists.")
    
    new_cat = EventCategory(
        code=req.code.lower().replace(" ", "_"),
        name=req.name,
        name_tamil=req.name_tamil,
        description=req.description,
        icon=req.icon or "calendar",
        display_order=req.display_order or 99,
        is_active=True
    )
    db.add(new_cat)
    db.flush()
    
    if req.event_types:
        for st_name in req.event_types:
            st = EventType(category_id=new_cat.id, name=st_name, description=f"Arrangements for {st_name}")
            db.add(st)
            
    audit = AuditLog(
        user_id=admin.id,
        action="CATEGORY_CREATED",
        entity_type="category",
        entity_id=new_cat.id
    )
    db.add(audit)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.post("/{category_id}/subtypes", response_model=EventTypeOut)
def add_subtype(
    category_id: int,
    req: EventTypeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    cat = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
        
    st = EventType(
        category_id=cat.id,
        name=req.name,
        name_tamil=req.name_tamil,
        description=req.description,
        is_active=True
    )
    db.add(st)
    db.commit()
    db.refresh(st)
    return st
