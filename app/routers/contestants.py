"""Router for contestant registration, documents, and fees."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models
from app import schemas

router = APIRouter(tags=["contestants"])


def _tenant_id(x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID")) -> int:
    """Extract tenant ID from header, defaulting to 1."""
    return x_tenant_id or 1


# ── Contestant CRUD ─────────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/contestants",
    response_model=list[schemas.ContestantOut],
)
def list_contestants(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
    skip: int = 0,
    limit: int = 100,
    division_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List contestants for a pageant, with optional filters."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    query = db.query(models.Contestant).filter(models.Contestant.pageant_id == pageant_id)

    if division_id is not None:
        query = query.filter(models.Contestant.division_id == division_id)
    if status is not None:
        query = query.filter(models.Contestant.status == status)

    return query.offset(skip).limit(limit).all()


@router.post(
    "/pageants/{pageant_id}/contestants",
    response_model=schemas.ContestantOut,
    status_code=201,
)
def register_contestant(
    pageant_id: int,
    payload: schemas.ContestantCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Register a new contestant for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    # If division_id provided, verify it belongs to the pageant
    if payload.division_id is not None:
        division = (
            db.query(models.AgeDivision)
            .filter(
                models.AgeDivision.id == payload.division_id,
                models.AgeDivision.pageant_id == pageant_id,
            )
            .first()
        )
        if not division:
            raise HTTPException(status_code=404, detail="Age division not found for this pageant")

    # Auto-assign contestant number (next available)
    max_num = (
        db.query(models.Contestant.contestant_number)
        .filter(models.Contestant.pageant_id == pageant_id)
        .order_by(models.Contestant.contestant_number.desc())
        .first()
    )
    next_number = (max_num[0] + 1) if max_num and max_num[0] is not None else 1

    contestant = models.Contestant(
        **payload.model_dump(),
        pageant_id=pageant_id,
        contestant_number=next_number,
    )
    db.add(contestant)
    db.commit()
    db.refresh(contestant)
    return contestant


@router.get("/contestants/{contestant_id}", response_model=schemas.ContestantDetail)
def get_contestant(
    contestant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Get full contestant detail by ID."""
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")
    return contestant


@router.patch("/contestants/{contestant_id}", response_model=schemas.ContestantDetail)
def update_contestant(
    contestant_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Update contestant fields (partial update).

    Accepts a JSON body with any subset of ContestantDetail fields.
    """
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    # Whitelist of updatable fields on the model
    updatable = {
        "division_id", "first_name", "last_name", "age", "birthdate",
        "address", "phone", "email", "emergency_contact", "photo_url",
        "platform_statement", "bio", "dressing_area",
    }
    for field, value in payload.items():
        if field in updatable:
            setattr(contestant, field, value)

    db.commit()
    db.refresh(contestant)
    return contestant


# ── Check-in ────────────────────────────────────────────────────────────


@router.post("/contestants/{contestant_id}/check-in", response_model=schemas.ContestantDetail)
def check_in_contestant(
    contestant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Check in a contestant (marks status as checked_in and records timestamp)."""
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    if contestant.status == models.ContestantStatus.checked_in:
        raise HTTPException(status_code=409, detail="Contestant is already checked in")

    contestant.status = models.ContestantStatus.checked_in
    contestant.checked_in_at = datetime.utcnow()
    db.commit()
    db.refresh(contestant)
    return contestant


# ── Documents ────────────────────────────────────────────────────────────


@router.get("/contestants/{contestant_id}/documents", response_model=list[dict])
def list_documents(
    contestant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """List all documents for a contestant."""
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    return [
        {
            "id": d.id,
            "contestant_id": d.contestant_id,
            "doc_type": d.doc_type,
            "file_url": d.file_url,
            "signed_date": d.signed_date.isoformat() if d.signed_date else None,
            "version": d.version,
        }
        for d in contestant.documents
    ]


@router.post("/contestants/{contestant_id}/documents", response_model=dict, status_code=201)
def add_document(
    contestant_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Add a document to a contestant.

    Expects JSON body with: doc_type (str), file_url (str), signed_date (str, optional).
    """
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    doc = models.ContestantDocument(
        contestant_id=contestant_id,
        doc_type=payload.get("doc_type"),
        file_url=payload.get("file_url"),
        signed_date=payload.get("signed_date"),
        version=payload.get("version", 1),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": doc.id,
        "contestant_id": doc.contestant_id,
        "doc_type": doc.doc_type,
        "file_url": doc.file_url,
        "signed_date": doc.signed_date.isoformat() if doc.signed_date else None,
        "version": doc.version,
    }


# ── Fees ────────────────────────────────────────────────────────────────


@router.get("/contestants/{contestant_id}/fees", response_model=list[dict])
def list_fees(
    contestant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """List all registration fees for a contestant."""
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    return [
        {
            "id": f.id,
            "contestant_id": f.contestant_id,
            "fee_type": f.fee_type,
            "amount": f.amount,
            "status": f.status.value if hasattr(f.status, "value") else f.status,
            "payment_method": f.payment_method,
            "payment_date": f.payment_date.isoformat() if f.payment_date else None,
            "receipt_sent": f.receipt_sent,
        }
        for f in contestant.fees
    ]


@router.post("/contestants/{contestant_id}/fees", response_model=dict, status_code=201)
def add_fee(
    contestant_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Add a registration fee to a contestant.

    Expects JSON body with: fee_type (str), amount (float), payment_method (str, optional).
    """
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    fee = models.RegistrationFee(
        contestant_id=contestant_id,
        fee_type=payload.get("fee_type"),
        amount=payload.get("amount"),
        payment_method=payload.get("payment_method"),
    )
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return {
        "id": fee.id,
        "contestant_id": fee.contestant_id,
        "fee_type": fee.fee_type,
        "amount": fee.amount,
        "status": fee.status.value if hasattr(fee.status, "value") else fee.status,
        "payment_method": fee.payment_method,
        "payment_date": fee.payment_date.isoformat() if fee.payment_date else None,
        "receipt_sent": fee.receipt_sent,
    }


@router.patch("/contestants/{contestant_id}/fees/{fee_id}", response_model=dict)
def update_fee_payment(
    contestant_id: int,
    fee_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Update a registration fee's payment status.

    Accepts: status (str), payment_method (str), payment_date (str), receipt_sent (bool).
    """
    contestant = (
        db.query(models.Contestant)
        .join(models.Pageant)
        .filter(
            models.Contestant.id == contestant_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found")

    fee = (
        db.query(models.RegistrationFee)
        .filter(
            models.RegistrationFee.id == fee_id,
            models.RegistrationFee.contestant_id == contestant_id,
        )
        .first()
    )
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")

    # Map status string to enum if provided
    if "status" in payload:
        status_str = payload["status"]
        if status_str == "paid":
            fee.status = models.FeeStatus.paid
        elif status_str == "pending":
            fee.status = models.FeeStatus.pending
        elif status_str == "refunded":
            fee.status = models.FeeStatus.refunded

    if "payment_method" in payload:
        fee.payment_method = payload["payment_method"]
    if "payment_date" in payload:
        fee.payment_date = payload["payment_date"]
    if "receipt_sent" in payload:
        fee.receipt_sent = payload["receipt_sent"]

    db.commit()
    db.refresh(fee)
    return {
        "id": fee.id,
        "contestant_id": fee.contestant_id,
        "fee_type": fee.fee_type,
        "amount": fee.amount,
        "status": fee.status.value if hasattr(fee.status, "value") else fee.status,
        "payment_method": fee.payment_method,
        "payment_date": fee.payment_date.isoformat() if fee.payment_date else None,
        "receipt_sent": fee.receipt_sent,
    }