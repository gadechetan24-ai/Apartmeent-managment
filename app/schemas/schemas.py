from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.models import UserRole, ApartmentStatus, PaymentStatus, MaintenanceStatus


# ── User Schemas ──────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.tenant


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Building Schemas ──────────────────────────────────────
class BuildingBase(BaseModel):
    name: str
    address: str
    city: str
    total_floors: int = 1
    amenities: Optional[str] = None


class BuildingCreate(BuildingBase):
    pass


class BuildingOut(BuildingBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Apartment Schemas ─────────────────────────────────────
class ApartmentBase(BaseModel):
    unit_number: str
    floor: int
    bedrooms: int = 1
    bathrooms: float = 1.0
    area_sqft: float
    rent_amount: float
    status: ApartmentStatus = ApartmentStatus.available
    description: Optional[str] = None
    building_id: int
    tenant_id: Optional[int] = None
    lease_start: Optional[datetime] = None
    lease_end: Optional[datetime] = None


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentUpdate(BaseModel):
    status: Optional[ApartmentStatus] = None
    tenant_id: Optional[int] = None
    rent_amount: Optional[float] = None
    lease_start: Optional[datetime] = None
    lease_end: Optional[datetime] = None
    description: Optional[str] = None


class ApartmentOut(ApartmentBase):
    id: int
    created_at: datetime
    building: Optional[BuildingOut] = None
    tenant: Optional[UserOut] = None

    model_config = {"from_attributes": True}


# ── Payment Schemas ───────────────────────────────────────
class PaymentBase(BaseModel):
    amount: float
    due_date: datetime
    description: Optional[str] = None
    apartment_id: int
    tenant_id: int


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    paid_date: Optional[datetime] = None


class PaymentOut(PaymentBase):
    id: int
    paid_date: Optional[datetime]
    status: PaymentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Maintenance Schemas ───────────────────────────────────
class MaintenanceBase(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    apartment_id: int


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    status: Optional[MaintenanceStatus] = None
    priority: Optional[str] = None


class MaintenanceOut(MaintenanceBase):
    id: int
    status: MaintenanceStatus
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Notification Schemas ──────────────────────────────────
class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Dashboard Stats ───────────────────────────────────────
class DashboardStats(BaseModel):
    total_apartments: int
    occupied: int
    available: int
    maintenance: int
    total_tenants: int
    monthly_revenue: float
    pending_payments: int
    open_maintenance: int
