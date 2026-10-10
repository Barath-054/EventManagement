import json
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.database import get_db
from backend.models import (
    Quotation, QuotationItem, QuotationRevision, Event,
    Service, EventService, User, AuditLog
)
from backend.schemas import (
    QuotationOut, QuotationItemOut, QuotationChangeRequest,
    ServiceSelection
)
from backend.pricing_engine import pricing_engine
from backend.auth import get_current_user

router = APIRouter(prefix="/api/quotations", tags=["Quotations & Pricing"])

class QuotationPreviewRequest(BaseModel):
    event_id: Optional[int] = None
    attendees: int = 50
    services: List[ServiceSelection]
    discount_amount: float = 0.0

class QuotationGenerateRequest(BaseModel):
    event_id: int
    services: Optional[List[ServiceSelection]] = None
    discount_amount: float = 0.0

@router.post("/preview")
def preview_quotation(req: QuotationPreviewRequest, db: Session = Depends(get_db)):
    """
    Real-time dynamic price calculation for client customizations.
    """
    items_to_calc = []
    for s_sel in req.services:
        svc = db.query(Service).filter(Service.id == s_sel.service_id).first()
        if svc:
            items_to_calc.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category_name": svc.service_category.name if svc.service_category else "General",
                "unit_type": svc.unit_type,
                "unit_price": svc.base_price,
                "quantity": s_sel.quantity
            })
            
    calc_res = pricing_engine.calculate_quotation(
        items=items_to_calc,
        attendees=req.attendees,
        discount_amount=req.discount_amount
    )
    return calc_res

@router.post("/generate", response_model=QuotationOut)
def generate_quotation(
    req: QuotationGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if current_user.role != "admin" and event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to generate quotation for this event.")

    # Determine services
    items_to_calc = []
    if req.services:
        for s_sel in req.services:
            svc = db.query(Service).filter(Service.id == s_sel.service_id).first()
            if svc:
                items_to_calc.append({
                    "service_id": svc.id,
                    "service_name": svc.name,
                    "category_name": svc.service_category.name if svc.service_category else "General",
                    "unit_type": svc.unit_type,
                    "unit_price": svc.base_price,
                    "quantity": s_sel.quantity
                })
    else:
        # Use existing attached event services
        for es in event.selected_services:
            if es.service and es.is_selected:
                items_to_calc.append({
                    "service_id": es.service.id,
                    "service_name": es.service.name,
                    "category_name": es.service.service_category.name if es.service.service_category else "General",
                    "unit_type": es.service.unit_type,
                    "unit_price": es.service.base_price,
                    "quantity": es.quantity
                })

    if not items_to_calc:
        raise HTTPException(status_code=400, detail="Cannot generate quotation without any selected services.")

    calc_res = pricing_engine.calculate_quotation(
        items=items_to_calc,
        attendees=event.expected_attendees,
        discount_amount=req.discount_amount
    )

    quote_number = f"QT-CBE-{datetime.datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    valid_until = (datetime.datetime.utcnow() + datetime.timedelta(days=15)).strftime("%Y-%m-%d")

    quotation = Quotation(
        quotation_number=quote_number,
        event_id=event.id,
        version=1,
        subtotal=calc_res["subtotal"],
        tax_rate=calc_res["tax_rate"],
        tax_amount=calc_res["tax_amount"],
        discount_amount=calc_res["discount_amount"],
        grand_total=calc_res["grand_total"],
        advance_required=calc_res["advance_required"],
        status="pending",
        valid_until=valid_until,
        snapshot_data_json=json.dumps(calc_res)  # Immutable snapshot of prices and items!
    )
    db.add(quotation)
    db.flush()

    for itm in calc_res["items"]:
        q_item = QuotationItem(
            quotation_id=quotation.id,
            service_id=itm["service_id"],
            service_name=itm["service_name"],
            category_name=itm["category_name"],
            unit_type=itm["unit_type"],
            quantity=itm["quantity"],
            unit_price=itm["unit_price"],
            total_price=itm["total_price"]
        )
        db.add(q_item)

    event.status = "quoted"
    
    audit = AuditLog(
        user_id=current_user.id,
        action="QUOTATION_GENERATED",
        entity_type="quotation",
        entity_id=quotation.id,
        details_json=json.dumps({"grand_total": calc_res["grand_total"], "number": quote_number})
    )
    db.add(audit)
    db.commit()
    db.refresh(quotation)

    return _format_quotation_out(quotation, event)

@router.post("/{quotation_id}/approve", response_model=QuotationOut)
def approve_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found.")
    if current_user.role != "admin" and quotation.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to approve this quotation.")

    quotation.status = "approved"
    quotation.event.status = "approved"

    audit = AuditLog(
        user_id=current_user.id,
        action="QUOTATION_APPROVED",
        entity_type="quotation",
        entity_id=quotation.id
    )
    db.add(audit)
    db.commit()
    db.refresh(quotation)

    return _format_quotation_out(quotation, quotation.event)

@router.post("/{quotation_id}/request-change", response_model=QuotationOut)
def request_quotation_change(
    quotation_id: int,
    req: QuotationChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found.")
    if current_user.role != "admin" and quotation.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to request changes.")

    previous_total = quotation.grand_total

    # If user provided modified services, recalculate
    if req.modified_services:
        items_to_calc = []
        for s_sel in req.modified_services:
            svc = db.query(Service).filter(Service.id == s_sel.service_id).first()
            if svc:
                items_to_calc.append({
                    "service_id": svc.id,
                    "service_name": svc.name,
                    "category_name": svc.service_category.name if svc.service_category else "General",
                    "unit_type": svc.unit_type,
                    "unit_price": svc.base_price,
                    "quantity": s_sel.quantity
                })
        
        calc_res = pricing_engine.calculate_quotation(
            items=items_to_calc,
            attendees=quotation.event.expected_attendees,
            discount_amount=quotation.discount_amount
        )

        quotation.version += 1
        quotation.subtotal = calc_res["subtotal"]
        quotation.tax_amount = calc_res["tax_amount"]
        quotation.grand_total = calc_res["grand_total"]
        quotation.advance_required = calc_res["advance_required"]
        quotation.snapshot_data_json = json.dumps(calc_res)

        # Replace items
        db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation.id).delete()
        for itm in calc_res["items"]:
            q_item = QuotationItem(
                quotation_id=quotation.id,
                service_id=itm["service_id"],
                service_name=itm["service_name"],
                category_name=itm["category_name"],
                unit_type=itm["unit_type"],
                quantity=itm["quantity"],
                unit_price=itm["unit_price"],
                total_price=itm["total_price"]
            )
            db.add(q_item)

    quotation.status = "change_requested"

    # Record Revision
    rev = QuotationRevision(
        quotation_id=quotation.id,
        revision_number=quotation.version,
        change_summary=req.reason,
        requested_by=current_user.full_name,
        previous_total=previous_total,
        revised_total=quotation.grand_total
    )
    db.add(rev)

    audit = AuditLog(
        user_id=current_user.id,
        action="QUOTATION_REVISION_REQUESTED",
        entity_type="quotation",
        entity_id=quotation.id,
        details_json=json.dumps({"reason": req.reason, "version": quotation.version})
    )
    db.add(audit)
    db.commit()
    db.refresh(quotation)

    return _format_quotation_out(quotation, quotation.event)

@router.get("/{quotation_id}", response_model=QuotationOut)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found.")
    if current_user.role != "admin" and quotation.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this quotation.")

    return _format_quotation_out(quotation, quotation.event)

def _format_quotation_out(q: Quotation, ev: Event) -> QuotationOut:
    items = []
    for itm in q.items:
        items.append(QuotationItemOut(
            id=itm.id,
            service_id=itm.service_id,
            service_name=itm.service_name,
            category_name=itm.category_name,
            unit_type=itm.unit_type,
            quantity=itm.quantity,
            unit_price=itm.unit_price,
            total_price=itm.total_price
        ))
    return QuotationOut(
        id=q.id,
        quotation_number=q.quotation_number,
        event_id=q.event_id,
        event_title=ev.title if ev else "",
        category_name=ev.category.name if ev and ev.category else "",
        version=q.version,
        subtotal=q.subtotal,
        tax_rate=q.tax_rate,
        tax_amount=q.tax_amount,
        discount_amount=q.discount_amount,
        grand_total=q.grand_total,
        advance_required=q.advance_required,
        status=q.status,
        valid_until=q.valid_until,
        items=items,
        created_at=q.created_at
    )
