from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut, Token, LoginRequest, UserUpdate
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=Token, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


class LoginJSONRequest(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Incorrect email or password",
    )

    body = await request.json()
    email = body.get("email") or body.get("username")
    password = body.get("password")

    if not email or not password:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise credentials_exception


    token = create_access_token({"sub": user.email})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )



@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if update.full_name:
        current_user.full_name = update.full_name
    if update.phone is not None:
        current_user.phone = update.phone
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db.query(User).all()
