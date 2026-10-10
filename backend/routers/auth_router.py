from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, CustomerProfile, AuditLog
from backend.schemas import UserRegister, UserLogin, UserOut, TokenResponse
from backend.auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    hashed = get_password_hash(req.password)
    new_user = User(
        full_name=req.full_name,
        email=req.email.lower(),
        phone=req.phone,
        password_hash=hashed,
        role=req.role or "customer",
        is_active=True
    )
    db.add(new_user)
    db.flush()
    
    profile = CustomerProfile(
        user_id=new_user.id,
        organization_name=req.organization_name,
        preferred_locality=req.preferred_locality or "RS Puram"
    )
    db.add(profile)
    
    audit = AuditLog(
        user_id=new_user.id,
        action="USER_REGISTERED",
        entity_type="user",
        entity_id=new_user.id
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    
    user_out = UserOut(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        phone=new_user.phone,
        role=new_user.role,
        preferred_locality=profile.preferred_locality,
        organization_name=profile.organization_name
    )
    return TokenResponse(access_token=access_token, user=user_out)

@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
        
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    profile = user.profile
    
    user_out = UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        preferred_locality=profile.preferred_locality if profile else "RS Puram",
        organization_name=profile.organization_name if profile else None
    )
    return TokenResponse(access_token=access_token, user=user_out)

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    profile = current_user.profile
    return UserOut(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        preferred_locality=profile.preferred_locality if profile else "RS Puram",
        organization_name=profile.organization_name if profile else None
    )
