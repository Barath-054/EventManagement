import uuid
import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Quotation, Payment, Booking, EventTask, User, AuditLog
from backend.schemas import PaymentRequest, PaymentOut
from backend.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments & Advance Gateway"])

@router.post("/process-advance", response_model=PaymentOut)
def process_advance_payment(
    req: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quotation = db.query(Quotation).filter(Quotation.id == req.quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found.")
    if current_user.role != "admin" and quotation.event.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to pay for this quotation.")

    pay_amount = quotation.advance_required if req.payment_type == "advance" else quotation.grand_total

    # Mock gateway transaction reference
    txn_ref = f"TXN-{req.payment_method.upper()}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:6].upper()}"
    
    payment = Payment(
        quotation_id=quotation.id,
        transaction_reference=txn_ref,
        payment_type=req.payment_type,
        payment_method=req.payment_method,
        amount=pay_amount,
        status="completed",
        gateway_response_json=json.dumps({
            "gateway": "Coimbatore Mock Razorpay/UPI Gateway",
            "vpa": req.upi_id or "customer@okaxis",
            "bank_ref": f"BANK-{uuid.uuid4().hex[:8].upper()}",
            "verified": True
        })
    )
    db.add(payment)
    db.flush()

    # Update Quotation & Event status
    quotation.status = "booked"
    event = quotation.event
    event.status = "booked"

    # Create Booking if not already created
    booking = db.query(Booking).filter(Booking.quotation_id == quotation.id).first()
    if not booking:
        booking_ref = f"BK-CBE-{datetime.datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        balance = max(0.0, quotation.grand_total - pay_amount)
        
        booking = Booking(
            quotation_id=quotation.id,
            event_id=event.id,
            booking_reference=booking_ref,
            status="confirmed",
            advance_paid=pay_amount,
            balance_due=balance,
            confirmed_at=datetime.datetime.utcnow()
        )
        db.add(booking)
        db.flush()

        # Seed milestone preparation tasks for Coimbatore event execution
        event_tasks = [
            ("Venue Inspection & Locality Clearance", "venue", "RS Puram/Gandhipuram Field Liaison", "Day -10"),
            ("Vendor Assignment & Customization Sign-off", "vendors", "Event Coordinator", "Day -7"),
            ("Audio-Visual & Acoustic Sound Check", "technical", "Sharp AV Sound Engineer", "Day -2"),
            ("Stage & Floral Decoration Ingress Setup", "decor", "Kavitha Decors Lead", "Day -1"),
            ("On-Day Event Execution & Emcee Briefing", "execution", "Lead Event Director", "Day 0"),
            ("Post-Event Logistics Clearance & Feedback", "wrapup", "Client Relationship Lead", "Day +1")
        ]
        
        for task_title, task_cat, assignee, due in event_tasks:
            t = EventTask(
                booking_id=booking.id,
                title=task_title,
                category=task_cat,
                status="pending",
                assigned_to=assignee,
                due_date=due
            )
            db.add(t)

    audit = AuditLog(
        user_id=current_user.id,
        action="ADVANCE_PAYMENT_COMPLETED",
        entity_type="payment",
        entity_id=payment.id,
        details_json=json.dumps({"amount": pay_amount, "txn": txn_ref, "method": req.payment_method})
    )
    db.add(audit)
    db.commit()
    db.refresh(payment)

    return PaymentOut(
        id=payment.id,
        quotation_id=payment.quotation_id,
        transaction_reference=payment.transaction_reference,
        payment_type=payment.payment_type,
        payment_method=payment.payment_method,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at
    )
