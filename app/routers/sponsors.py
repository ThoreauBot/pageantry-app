"""Sponsor, donation, and barter agreement endpoints for the Pageantry Application."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import (
    Pageant,
    Sponsor,
    SponsorshipTier,
    SponsorshipAgreement,
    Donation,
    BarterAgreement,
)
from app.schemas import (
    SponsorCreate,
    SponsorUpdate,
    SponsorOut,
    SponsorshipTierCreate,
    SponsorshipTierOut,
    SponsorshipAgreementCreate,
    SponsorshipAgreementOut,
    DonationCreate,
    DonationOut,
    BarterAgreementCreate,
    BarterAgreementOut,
)

router = APIRouter(tags=["sponsors"])


# ── Sponsors ────────────────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/sponsors",
    response_model=List[SponsorOut],
)
def list_sponsors(pageant_id: int, db: Session = Depends(get_db)):
    """List sponsors for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    sponsors = (
        db.query(Sponsor)
        .filter(Sponsor.pageant_id == pageant_id)
        .all()
    )
    return sponsors


@router.post(
    "/pageants/{pageant_id}/sponsors",
    response_model=SponsorOut,
    status_code=status.HTTP_201_CREATED,
)
def create_sponsor(
    pageant_id: int,
    payload: SponsorCreate,
    db: Session = Depends(get_db),
):
    """Create a sponsor for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    sponsor = Sponsor(pageant_id=pageant_id, **payload.model_dump())
    db.add(sponsor)
    db.commit()
    db.refresh(sponsor)
    return sponsor


@router.get("/sponsors/{sponsor_id}", response_model=SponsorOut)
def get_sponsor(sponsor_id: int, db: Session = Depends(get_db)):
    """Get sponsor detail."""
    sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found",
        )
    return sponsor


@router.patch("/sponsors/{sponsor_id}", response_model=SponsorOut)
def update_sponsor(
    sponsor_id: int,
    payload: SponsorUpdate,
    db: Session = Depends(get_db),
):
    """Update a sponsor."""
    sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sponsor, field, value)
    db.commit()
    db.refresh(sponsor)
    return sponsor


# ── Sponsorship Tiers ───────────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/sponsorship-tiers",
    response_model=SponsorshipTierOut,
    status_code=status.HTTP_201_CREATED,
)
def create_sponsorship_tier(
    pageant_id: int,
    payload: SponsorshipTierCreate,
    db: Session = Depends(get_db),
):
    """Create a sponsorship tier for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    tier = SponsorshipTier(pageant_id=pageant_id, **payload.model_dump())
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@router.get(
    "/pageants/{pageant_id}/sponsorship-tiers",
    response_model=List[SponsorshipTierOut],
)
def list_sponsorship_tiers(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List sponsorship tiers for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    tiers = (
        db.query(SponsorshipTier)
        .filter(SponsorshipTier.pageant_id == pageant_id)
        .all()
    )
    return tiers


# ── Sponsorship Agreements ──────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/agreements",
    response_model=SponsorshipAgreementOut,
    status_code=status.HTTP_201_CREATED,
)
def create_sponsorship_agreement(
    pageant_id: int,
    payload: SponsorshipAgreementCreate,
    db: Session = Depends(get_db),
):
    """Create a sponsorship agreement for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    # Verify the sponsor belongs to this pageant
    sponsor = (
        db.query(Sponsor)
        .filter(
            Sponsor.id == payload.sponsor_id,
            Sponsor.pageant_id == pageant_id,
        )
        .first()
    )
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor not found for this pageant",
        )
    agreement = SponsorshipAgreement(**payload.model_dump())
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


@router.get(
    "/pageants/{pageant_id}/agreements",
    response_model=List[SponsorshipAgreementOut],
)
def list_sponsorship_agreements(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List sponsorship agreements for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    agreements = (
        db.query(SponsorshipAgreement)
        .join(Sponsor, SponsorshipAgreement.sponsor_id == Sponsor.id)
        .filter(Sponsor.pageant_id == pageant_id)
        .all()
    )
    return agreements


# ── Donations ───────────────────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/donations",
    response_model=DonationOut,
    status_code=status.HTTP_201_CREATED,
)
def record_donation(
    pageant_id: int,
    payload: DonationCreate,
    db: Session = Depends(get_db),
):
    """Record a donation for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    donation = Donation(pageant_id=pageant_id, **payload.model_dump())
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


@router.get(
    "/pageants/{pageant_id}/donations",
    response_model=List[DonationOut],
)
def list_donations(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List donations for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    donations = (
        db.query(Donation)
        .filter(Donation.pageant_id == pageant_id)
        .all()
    )
    return donations


# ── Barter Agreements ───────────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/barter",
    response_model=BarterAgreementOut,
    status_code=status.HTTP_201_CREATED,
)
def create_barter_agreement(
    pageant_id: int,
    payload: BarterAgreementCreate,
    db: Session = Depends(get_db),
):
    """Create a barter agreement for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    agreement = BarterAgreement(
        pageant_id=pageant_id, **payload.model_dump()
    )
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


@router.get(
    "/pageants/{pageant_id}/barter",
    response_model=List[BarterAgreementOut],
)
def list_barter_agreements(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List barter agreements for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    agreements = (
        db.query(BarterAgreement)
        .filter(BarterAgreement.pageant_id == pageant_id)
        .all()
    )
    return agreements