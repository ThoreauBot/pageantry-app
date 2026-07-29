"""Titleholder router: manage titleholders, appearances, appearance requests,
points, contract, and removal proceedings."""
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Appearance,
    AppearanceRequest,
    AppearanceStatus,
    Titleholder,
    TitleholderContract,
    TitleholderPoint,
    TitleholderStatus,
    TitleRemovalProceeding,
)
from app.schemas import AppearanceCreate, AppearanceOut, TitleholderCreate, TitleholderOut

router = APIRouter(tags=["titleholders"])


# ── Additional schemas ──────────────────────────────────────────────

class TitleholderUpdate(BaseModel):
    status: str


class ContractCreate(BaseModel):
    signed_date: Optional[date] = None
    terms: Optional[str] = None
    file_url: Optional[str] = None


class ContractOut(BaseModel):
    id: int
    titleholder_id: int
    signed_date: Optional[date]
    terms: Optional[str]
    file_url: Optional[str]

    class Config:
        from_attributes = True


class AppearanceRequestCreate(BaseModel):
    requester_name: Optional[str] = None
    requester_contact: Optional[str] = None
    event_name: str
    date: date


class AppearanceRequestOut(BaseModel):
    id: int
    titleholder_id: int
    requester_name: Optional[str]
    requester_contact: Optional[str]
    event_name: str
    date: date
    status: str

    class Config:
        from_attributes = True


class AppearanceRequestPatch(BaseModel):
    status: str  # "approved" or "declined"


class TitleholderPointCreate(BaseModel):
    point_value: int
    reason: Optional[str] = None
    category: Optional[str] = None
    point_date: Optional[date] = None


class TitleholderPointOut(BaseModel):
    id: int
    titleholder_id: int
    point_value: int
    reason: Optional[str]
    point_date: date
    category: Optional[str]

    class Config:
        from_attributes = True


class RemovalProceedingCreate(BaseModel):
    grounds: Optional[str] = None
    documentation_notes: Optional[str] = None


class RemovalProceedingOut(BaseModel):
    id: int
    titleholder_id: int
    date_initiated: datetime
    grounds: Optional[str]
    documentation_notes: Optional[str]
    communication_log: Optional[str]
    outcome: Optional[str]
    effective_date: Optional[date]

    class Config:
        from_attributes = True


# ── Helpers ─────────────────────────────────────────────────────────

def get_titleholder_or_404(db: Session, titleholder_id: int) -> Titleholder:
    th = db.query(Titleholder).filter(Titleholder.id == titleholder_id).first()
    if not th:
        raise HTTPException(status_code=404, detail="Titleholder not found")
    return th


# ── Titleholder CRUD ────────────────────────────────────────────────

@router.get(
    "/pageants/{pageant_id}/titleholders",
    response_model=List[TitleholderOut],
)
def list_titleholders(pageant_id: int, db: Session = Depends(get_db)):
    """List all titleholders for a pageant (via contestant.pageant_id)."""
    holders = (
        db.query(Titleholder)
        .join(Titleholder.contestant)
        .filter(Titleholder.contestant.has(pageant_id=pageant_id))
        .all()
    )
    return holders


@router.post(
    "/pageants/{pageant_id}/titleholders",
    response_model=TitleholderOut,
    status_code=201,
)
def create_titleholder(
    pageant_id: int,
    payload: TitleholderCreate,
    db: Session = Depends(get_db),
):
    """Create a new titleholder for a pageant."""
    th = Titleholder(
        contestant_id=payload.contestant_id,
        title=payload.title,
        reign_start_date=payload.reign_start_date,
        reign_end_date=payload.reign_end_date,
    )
    db.add(th)
    db.commit()
    db.refresh(th)
    return th


@router.get("/titleholders/{titleholder_id}", response_model=TitleholderOut)
def get_titleholder(titleholder_id: int, db: Session = Depends(get_db)):
    """Get a single titleholder by id."""
    return get_titleholder_or_404(db, titleholder_id)


@router.patch("/titleholders/{titleholder_id}", response_model=TitleholderOut)
def update_titleholder_status(
    titleholder_id: int,
    payload: TitleholderUpdate,
    db: Session = Depends(get_db),
):
    """Update titleholder status (active, completed, removed, resigned)."""
    th = get_titleholder_or_404(db, titleholder_id)
    if payload.status not in (
        TitleholderStatus.active.value,
        TitleholderStatus.completed.value,
        TitleholderStatus.removed.value,
        TitleholderStatus.resigned.value,
    ):
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
    th.status = payload.status
    db.commit()
    db.refresh(th)
    return th


# ── Contract ────────────────────────────────────────────────────────

@router.put("/titleholders/{titleholder_id}/contract", response_model=ContractOut)
def set_contract(
    titleholder_id: int,
    payload: ContractCreate,
    db: Session = Depends(get_db),
):
    """Upload or set the titleholder contract."""
    th = get_titleholder_or_404(db, titleholder_id)
    if th.contract:
        c = th.contract
        c.signed_date = payload.signed_date or c.signed_date
        c.terms = payload.terms or c.terms
        c.file_url = payload.file_url or c.file_url
    else:
        c = TitleholderContract(
            titleholder_id=titleholder_id,
            signed_date=payload.signed_date,
            terms=payload.terms,
            file_url=payload.file_url,
        )
        db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ── Appearances ─────────────────────────────────────────────────────

@router.post(
    "/titleholders/{titleholder_id}/appearances",
    response_model=AppearanceOut,
    status_code=201,
)
def log_appearance(
    titleholder_id: int,
    payload: AppearanceCreate,
    db: Session = Depends(get_db),
):
    """Log a new appearance for a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    app = Appearance(
        titleholder_id=titleholder_id,
        event_name=payload.event_name,
        date=payload.date,
        location=payload.location,
        appearance_type=payload.appearance_type,
        notes=payload.notes,
        hours_logged=payload.hours_logged,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get(
    "/titleholders/{titleholder_id}/appearances",
    response_model=List[AppearanceOut],
)
def list_appearances(titleholder_id: int, db: Session = Depends(get_db)):
    """List all appearances for a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    apps = (
        db.query(Appearance)
        .filter(Appearance.titleholder_id == titleholder_id)
        .order_by(Appearance.date.desc())
        .all()
    )
    return apps


# ── Appearance Requests ─────────────────────────────────────────────

@router.post(
    "/titleholders/{titleholder_id}/appearance-requests",
    response_model=AppearanceRequestOut,
    status_code=201,
)
def submit_appearance_request(
    titleholder_id: int,
    payload: AppearanceRequestCreate,
    db: Session = Depends(get_db),
):
    """Submit an appearance request for a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    req = AppearanceRequest(
        titleholder_id=titleholder_id,
        requester_name=payload.requester_name,
        requester_contact=payload.requester_contact,
        event_name=payload.event_name,
        date=payload.date,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get(
    "/titleholders/{titleholder_id}/appearance-requests",
    response_model=List[AppearanceRequestOut],
)
def list_appearance_requests(titleholder_id: int, db: Session = Depends(get_db)):
    """List all appearance requests for a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    reqs = (
        db.query(AppearanceRequest)
        .filter(AppearanceRequest.titleholder_id == titleholder_id)
        .order_by(AppearanceRequest.date.desc())
        .all()
    )
    return reqs


@router.patch(
    "/appearance-requests/{request_id}",
    response_model=AppearanceRequestOut,
)
def approve_or_decline_request(
    request_id: int,
    payload: AppearanceRequestPatch,
    db: Session = Depends(get_db),
):
    """Approve or decline an appearance request."""
    req = (
        db.query(AppearanceRequest).filter(AppearanceRequest.id == request_id).first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Appearance request not found")

    valid = {AppearanceStatus.approved.value, AppearanceStatus.declined.value}
    if payload.status not in valid:
        raise HTTPException(
            status_code=422,
            detail=f"Status must be one of: {', '.join(valid)}",
        )
    req.status = payload.status
    db.commit()
    db.refresh(req)
    return req


# ── Points ──────────────────────────────────────────────────────────

@router.post(
    "/titleholders/{titleholder_id}/points",
    response_model=TitleholderPointOut,
    status_code=201,
)
def add_points(
    titleholder_id: int,
    payload: TitleholderPointCreate,
    db: Session = Depends(get_db),
):
    """Add points to a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    pt = TitleholderPoint(
        titleholder_id=titleholder_id,
        point_value=payload.point_value,
        reason=payload.reason,
        category=payload.category,
        point_date=payload.point_date or date.today(),
    )
    db.add(pt)
    db.commit()
    db.refresh(pt)
    return pt


@router.get(
    "/titleholders/{titleholder_id}/points",
    response_model=List[TitleholderPointOut],
)
def list_points(titleholder_id: int, db: Session = Depends(get_db)):
    """List all points for a titleholder."""
    get_titleholder_or_404(db, titleholder_id)
    pts = (
        db.query(TitleholderPoint)
        .filter(TitleholderPoint.titleholder_id == titleholder_id)
        .order_by(TitleholderPoint.point_date.desc())
        .all()
    )
    return pts


# ── Removal Proceeding ──────────────────────────────────────────────

@router.post(
    "/titleholders/{titleholder_id}/removal",
    response_model=RemovalProceedingOut,
    status_code=201,
)
def initiate_removal(
    titleholder_id: int,
    payload: RemovalProceedingCreate,
    db: Session = Depends(get_db),
):
    """Initiate a removal proceeding for a titleholder."""
    th = get_titleholder_or_404(db, titleholder_id)
    if th.removal_proceeding:
        raise HTTPException(
            status_code=409,
            detail="A removal proceeding already exists for this titleholder",
        )
    proc = TitleRemovalProceeding(
        titleholder_id=titleholder_id,
        grounds=payload.grounds,
        documentation_notes=payload.documentation_notes,
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc


@router.get(
    "/titleholders/{titleholder_id}/removal",
    response_model=RemovalProceedingOut,
)
def get_removal_proceeding(titleholder_id: int, db: Session = Depends(get_db)):
    """Get the removal proceeding for a titleholder."""
    th = get_titleholder_or_404(db, titleholder_id)
    if not th.removal_proceeding:
        raise HTTPException(
            status_code=404,
            detail="No removal proceeding found for this titleholder",
        )
    return th.removal_proceeding