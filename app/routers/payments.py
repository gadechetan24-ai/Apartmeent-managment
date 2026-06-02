from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.models import Payment, User, PaymentStatus
from app.schemas.schemas import PaymentCreate, PaymentOut, PaymentUpdate
from app.core.security import get_current_active_user, require_admin

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role in ("admin", "manager"):
        return db.query(Payment).all()
    return db.query(Payment).filter(Payment.tenant_id == current_user.id).all()


@router.post("/", response_model=PaymentOut, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    p = Payment(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{payment_id}/pay", response_model=PaymentOut)
def mark_paid(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    if current_user.role not in ("admin", "manager") and p.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    p.status = PaymentStatus.paid
    p.paid_date = datetime.utcnow()
    db.commit()
    db.refresh(p)
    return p


@router.get("/stats/summary")
def payment_summary(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total = db.query(Payment).count()
    paid = db.query(Payment).filter(Payment.status == PaymentStatus.paid).count()
    pending = db.query(Payment).filter(Payment.status == PaymentStatus.pending).count()
    overdue = db.query(Payment).filter(Payment.status == PaymentStatus.overdue).count()
    paid_payments = db.query(Payment).filter(Payment.status == PaymentStatus.paid).all()
    total_revenue = sum(p.amount for p in paid_payments)
    return {"total": total, "paid": paid, "pending": pending, "overdue": overdue, "total_revenue": total_revenue}
