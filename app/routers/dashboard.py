from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Apartment, User, Payment, MaintenanceRequest, ApartmentStatus, PaymentStatus, MaintenanceStatus
from app.schemas.schemas import DashboardStats
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    total_apts = db.query(Apartment).count()
    occupied = db.query(Apartment).filter(Apartment.status == ApartmentStatus.occupied).count()
    available = db.query(Apartment).filter(Apartment.status == ApartmentStatus.available).count()
    maint_apts = db.query(Apartment).filter(Apartment.status == ApartmentStatus.maintenance).count()
    total_tenants = db.query(User).filter(User.role == "tenant").count()

    paid_this_month = db.query(Payment).filter(Payment.status == PaymentStatus.paid).all()
    monthly_rev = sum(p.amount for p in paid_this_month)

    pending_pay = db.query(Payment).filter(Payment.status == PaymentStatus.pending).count()
    open_maint = db.query(MaintenanceRequest).filter(MaintenanceRequest.status == MaintenanceStatus.open).count()

    return DashboardStats(
        total_apartments=total_apts,
        occupied=occupied,
        available=available,
        maintenance=maint_apts,
        total_tenants=total_tenants,
        monthly_revenue=monthly_rev,
        pending_payments=pending_pay,
        open_maintenance=open_maint,
    )
