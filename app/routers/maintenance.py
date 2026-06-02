from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import MaintenanceRequest, User, MaintenanceStatus
from app.schemas.schemas import MaintenanceCreate, MaintenanceOut, MaintenanceUpdate
from app.core.security import get_current_active_user, require_admin

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/", response_model=list[MaintenanceOut])
def list_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role in ("admin", "manager"):
        return db.query(MaintenanceRequest).all()
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.tenant_id == current_user.id).all()


@router.post("/", response_model=MaintenanceOut, status_code=201)
def create_request(data: MaintenanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    req = MaintenanceRequest(**data.model_dump(), tenant_id=current_user.id)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.put("/{req_id}", response_model=MaintenanceOut)
def update_request(req_id: int, data: MaintenanceUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(req, field, value)
    db.commit()
    db.refresh(req)
    return req


@router.delete("/{req_id}", status_code=204)
def delete_request(req_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    db.delete(req)
    db.commit()
