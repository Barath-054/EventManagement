import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Service, ServiceCategory, AuditLog, User
from backend.schemas import ServiceOut, ServiceCreate
from backend.auth import require_admin

router = APIRouter(prefix="/api/services", tags=["Services Catalog"])

@router.get("", response_model=List[ServiceOut])
def get_services(
    category_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Service).filter(Service.is_active == True)
    services = query.all()
    
    result = []
    for s in services:
        eligible_cats = []
        try:
            eligible_cats = json.loads(s.eligible_categories_json)
        except Exception:
            pass
            
        # Filter if category_code is specified
        if category_code:
            target = category_code.lower()
            if "*" not in eligible_cats and target not in [c.lower() for c in eligible_cats]:
                continue
                
        result.append(ServiceOut(
            id=s.id,
            service_category_id=s.service_category_id,
            category_name=s.service_category.name if s.service_category else "",
            code=s.code,
            name=s.name,
            description=s.description,
            unit_type=s.unit_type,
            base_price=s.base_price,
            min_quantity=s.min_quantity,
            eligible_categories=eligible_cats,
            is_mandatory=s.is_mandatory,
            is_active=s.is_active
        ))
    return result

@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found.")
    eligible_cats = json.loads(s.eligible_categories_json) if s.eligible_categories_json else []
    return ServiceOut(
        id=s.id,
        service_category_id=s.service_category_id,
        category_name=s.service_category.name if s.service_category else "",
        code=s.code,
        name=s.name,
        description=s.description,
        unit_type=s.unit_type,
        base_price=s.base_price,
        min_quantity=s.min_quantity,
        eligible_categories=eligible_cats,
        is_mandatory=s.is_mandatory,
        is_active=s.is_active
    )

@router.post("", response_model=ServiceOut)
def create_service(
    req: ServiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    existing = db.query(Service).filter(Service.code == req.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Service with this code already exists.")
        
    s = Service(
        service_category_id=req.service_category_id,
        code=req.code,
        name=req.name,
        description=req.description,
        unit_type=req.unit_type,
        base_price=req.base_price,
        min_quantity=req.min_quantity or 1,
        eligible_categories_json=json.dumps(req.eligible_categories or ["*"]),
        is_mandatory=req.is_mandatory or False,
        is_active=True
    )
    db.add(s)
    db.flush()
    
    audit = AuditLog(
        user_id=admin.id,
        action="SERVICE_CREATED",
        entity_type="service",
        entity_id=s.id
    )
    db.add(audit)
    db.commit()
    db.refresh(s)
    
    return ServiceOut(
        id=s.id,
        service_category_id=s.service_category_id,
        category_name=s.service_category.name if s.service_category else "",
        code=s.code,
        name=s.name,
        description=s.description,
        unit_type=s.unit_type,
        base_price=s.base_price,
        min_quantity=s.min_quantity,
        eligible_categories=req.eligible_categories or ["*"],
        is_mandatory=s.is_mandatory,
        is_active=s.is_active
    )

@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    req: ServiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found.")
        
    s.name = req.name
    s.description = req.description
    s.unit_type = req.unit_type
    s.base_price = req.base_price
    s.min_quantity = req.min_quantity or 1
    s.eligible_categories_json = json.dumps(req.eligible_categories or ["*"])
    s.is_mandatory = req.is_mandatory or False
    
    audit = AuditLog(
        user_id=admin.id,
        action="SERVICE_UPDATED",
        entity_type="service",
        entity_id=s.id
    )
    db.add(audit)
    db.commit()
    db.refresh(s)
    
    return ServiceOut(
        id=s.id,
        service_category_id=s.service_category_id,
        category_name=s.service_category.name if s.service_category else "",
        code=s.code,
        name=s.name,
        description=s.description,
        unit_type=s.unit_type,
        base_price=s.base_price,
        min_quantity=s.min_quantity,
        eligible_categories=req.eligible_categories or ["*"],
        is_mandatory=s.is_mandatory,
        is_active=s.is_active
    )
