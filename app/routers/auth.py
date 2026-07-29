"""Auth router: tenant registration, login, and session info."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant
from app.schemas import TenantCreate, TenantLogin, TenantOut

router = APIRouter(prefix="/auth", tags=["auth"])


def get_tenant_id(x_tenant_id: int = Header(default=1, alias="X-Tenant-ID")) -> int:
    """Dependency: read the active tenant id from the X-Tenant-ID header."""
    return x_tenant_id


@router.post("/register", response_model=TenantOut, status_code=201)
def register(payload: TenantCreate, db: Session = Depends(get_db)):
    """Create a new tenant account."""
    existing = db.query(Tenant).filter(Tenant.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Simple plain-text password for now (no JWT, no hashing)
    tenant = Tenant(
        name=payload.name,
        email=payload.email,
        password_hash=payload.password,
        role=payload.role,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.post("/login", response_model=TenantOut)
def login(payload: TenantLogin, db: Session = Depends(get_db)):
    """Simple login — returns tenant info on email/password match (no JWT)."""
    tenant = db.query(Tenant).filter(Tenant.email == payload.email).first()
    if not tenant or tenant.password_hash != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return tenant


@router.get("/me", response_model=TenantOut)
def get_me(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
):
    """Return the current tenant's info based on X-Tenant-ID header."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant