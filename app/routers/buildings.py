from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Building, User
from app.schemas.schemas import BuildingCreate, BuildingOut
from app.core.security import get_current_active_user, require_admin

router = APIRouter(prefix="/api/buildings", tags=["buildings"])


@router.get("/", response_model=list[BuildingOut])
def list_buildings(db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    return db.query(Building).all()


@router.post("/", response_model=BuildingOut, status_code=201)
def create_building(data: BuildingCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    b = Building(**data.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.get("/{building_id}", response_model=BuildingOut)
def get_building(building_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    return b


@router.delete("/{building_id}", status_code=204)
def delete_building(building_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(b)
    db.commit()
