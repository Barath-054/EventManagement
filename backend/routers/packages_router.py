from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import EventPackage, PackageService, Service, EventCategory, User, AuditLog
from backend.schemas import EventPackageOut, PackageServiceItem, EventPackageCreate
from backend.auth import require_admin

router = APIRouter(prefix="/api/packages", tags=["Event Packages"])

@router.get("", response_model=List[EventPackageOut])
def get_packages(
    category_id: Optional[int] = None,
    category_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(EventPackage).filter(EventPackage.is_active == True)
    if category_id:
        query = query.filter(EventPackage.category_id == category_id)
    elif category_code:
        cat = db.query(EventCategory).filter(EventCategory.code == category_code.lower()).first()
        if cat:
            query = query.filter(EventPackage.category_id == cat.id)
            
    packages = query.all()
    results = []
    for pkg in packages:
        items = []
        for ps in pkg.package_services:
            if ps.service and ps.service.is_active:
                items.append(PackageServiceItem(
                    service_id=ps.service_id,
                    service_name=ps.service.name,
                    unit_type=ps.service.unit_type,
                    unit_price=ps.service.base_price,
                    included_quantity=ps.included_quantity,
                    is_customizable=ps.is_customizable
                ))
        results.append(EventPackageOut(
            id=pkg.id,
            category_id=pkg.category_id,
            category_code=pkg.category.code if pkg.category else None,
            tier=pkg.tier,
            name=pkg.name,
            description=pkg.description,
            base_price=pkg.base_price,
            attendee_limit=pkg.attendee_limit,
            is_active=pkg.is_active,
            included_services=items
        ))
    return results

@router.get("/{package_id}", response_model=EventPackageOut)
def get_package_detail(package_id: int, db: Session = Depends(get_db)):
    pkg = db.query(EventPackage).filter(EventPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found.")
    items = []
    for ps in pkg.package_services:
        if ps.service and ps.service.is_active:
            items.append(PackageServiceItem(
                service_id=ps.service_id,
                service_name=ps.service.name,
                unit_type=ps.service.unit_type,
                unit_price=ps.service.base_price,
                included_quantity=ps.included_quantity,
                is_customizable=ps.is_customizable
            ))
    return EventPackageOut(
        id=pkg.id,
        category_id=pkg.category_id,
        category_code=pkg.category.code if pkg.category else None,
        tier=pkg.tier,
        name=pkg.name,
        description=pkg.description,
        base_price=pkg.base_price,
        attendee_limit=pkg.attendee_limit,
        is_active=pkg.is_active,
        included_services=items
    )
