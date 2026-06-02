from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Apartment, User
from app.schemas.schemas import ApartmentCreate, ApartmentOut, ApartmentUpdate
from app.core.security import get_current_active_user, require_admin

router = APIRouter(prefix="/api/apartments", tags=["apartments"])


@router.get("/", response_model=list[ApartmentOut])
def list_apartments(db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    return db.query(Apartment).options(
        joinedload(Apartment.building),
        joinedload(Apartment.tenant)
    ).all()


@router.post("/", response_model=ApartmentOut, status_code=201)
def create_apartment(data: ApartmentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    apt = Apartment(**data.model_dump())
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return apt


@router.get("/{apt_id}", response_model=ApartmentOut)
def get_apartment(apt_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    apt = db.query(Apartment).options(
        joinedload(Apartment.building),
        joinedload(Apartment.tenant)
    ).filter(Apartment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apt


@router.put("/{apt_id}", response_model=ApartmentOut)
def update_apartment(apt_id: int, data: ApartmentUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    apt = db.query(Apartment).filter(Apartment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(apt, field, value)
    db.commit()
    db.refresh(apt)
    return apt


@router.delete("/{apt_id}", status_code=204)
def delete_apartment(apt_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    apt = db.query(Apartment).filter(Apartment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")
    db.delete(apt)
    db.commit()
