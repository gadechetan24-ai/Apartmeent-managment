from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    tenant = "tenant"


class ApartmentStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"


class MaintenanceStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.tenant)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    apartment = relationship("Apartment", back_populates="tenant", uselist=False, foreign_keys="Apartment.tenant_id")
    payments = relationship("Payment", back_populates="tenant")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")
    notifications = relationship("Notification", back_populates="user")


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    total_floors = Column(Integer, default=1)
    amenities = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    apartments = relationship("Apartment", back_populates="building")


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String(20), nullable=False)
    floor = Column(Integer, nullable=False)
    bedrooms = Column(Integer, default=1)
    bathrooms = Column(Float, default=1.0)
    area_sqft = Column(Float, nullable=False)
    rent_amount = Column(Float, nullable=False)
    status = Column(Enum(ApartmentStatus), default=ApartmentStatus.available)
    description = Column(Text, nullable=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lease_start = Column(DateTime, nullable=True)
    lease_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    building = relationship("Building", back_populates="apartments")
    tenant = relationship("User", back_populates="apartment", foreign_keys=[tenant_id])
    payments = relationship("Payment", back_populates="apartment")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="apartment")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    description = Column(String(255), nullable=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    apartment = relationship("Apartment", back_populates="payments")
    tenant = relationship("User", back_populates="payments")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.open)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    apartment = relationship("Apartment", back_populates="maintenance_requests")
    tenant = relationship("User", back_populates="maintenance_requests")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
