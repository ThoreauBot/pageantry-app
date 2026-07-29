"""Venue management endpoints for the Pageantry Application."""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import (
    Venue,
    VenueContract,
    VenueAmenity,
    VenueLayout,
    Pageant,
)
from app.schemas import (
    VenueCreate,
    VenueUpdate,
    VenueOut,
    VenueAmenityCreate,
    VenueAmenityOut,
    VenueContractCreate,
    VenueContractUpdate,
    VenueContractOut,
    VenueLayoutCreate,
    VenueLayoutOut,
)

router = APIRouter(tags=["venues"])


def _get_tenant_id(x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID")) -> int:
    """Extract tenant ID from header, defaulting to 1."""
    return x_tenant_id or 1


# ── Venue CRUD ──────────────────────────────────────────────────────────


@router.get("/venues", response_model=List[VenueOut])
def list_venues(db: Session = Depends(get_db)):
    """List all venues."""
    venues = db.query(Venue).all()
    return venues


@router.post("/venues", response_model=VenueOut, status_code=status.HTTP_201_CREATED)
def create_venue(
    payload: VenueCreate,
    db: Session = Depends(get_db),
):
    """Create a new venue."""
    venue = Venue(**payload.model_dump())
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue


@router.get("/venues/{venue_id}", response_model=VenueOut)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Get venue detail."""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )
    return venue


@router.patch("/venues/{venue_id}", response_model=VenueOut)
def update_venue(
    venue_id: int,
    payload: VenueUpdate,
    db: Session = Depends(get_db),
):
    """Update a venue."""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    db.commit()
    db.refresh(venue)
    return venue


# ── Venue Amenities ─────────────────────────────────────────────────────


@router.post(
    "/venues/{venue_id}/amenities",
    response_model=VenueAmenityOut,
    status_code=status.HTTP_201_CREATED,
)
def add_venue_amenity(
    venue_id: int,
    payload: VenueAmenityCreate,
    db: Session = Depends(get_db),
):
    """Add an amenity to a venue."""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )
    amenity = VenueAmenity(venue_id=venue_id, **payload.model_dump())
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    return amenity


@router.get(
    "/venues/{venue_id}/amenities",
    response_model=List[VenueAmenityOut],
)
def list_venue_amenities(
    venue_id: int,
    db: Session = Depends(get_db),
):
    """List amenities for a venue."""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )
    return venue.amenities


# ── Venue Contracts ─────────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/venue-contracts",
    response_model=List[VenueContractOut],
)
def list_venue_contracts(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List venue contracts for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    contracts = (
        db.query(VenueContract)
        .filter(VenueContract.pageant_id == pageant_id)
        .all()
    )
    return contracts


@router.post(
    "/pageants/{pageant_id}/venue-contracts",
    response_model=VenueContractOut,
    status_code=status.HTTP_201_CREATED,
)
def create_venue_contract(
    pageant_id: int,
    payload: VenueContractCreate,
    db: Session = Depends(get_db),
):
    """Create a venue contract for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    contract = VenueContract(pageant_id=pageant_id, **payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.patch(
    "/venue-contracts/{contract_id}",
    response_model=VenueContractOut,
)
def update_venue_contract(
    contract_id: int,
    payload: VenueContractUpdate,
    db: Session = Depends(get_db),
):
    """Update a venue contract."""
    contract = (
        db.query(VenueContract).filter(VenueContract.id == contract_id).first()
    )
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue contract not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    db.commit()
    db.refresh(contract)
    return contract


# ── Venue Layouts ───────────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/venue-layouts",
    response_model=List[VenueLayoutOut],
)
def get_venue_layouts(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """Get venue layouts for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    layouts = (
        db.query(VenueLayout)
        .filter(VenueLayout.pageant_id == pageant_id)
        .all()
    )
    return layouts


@router.post(
    "/pageants/{pageant_id}/venue-layouts",
    response_model=VenueLayoutOut,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_venue_layout(
    pageant_id: int,
    payload: VenueLayoutCreate,
    db: Session = Depends(get_db),
):
    """Create or update a venue layout for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )

    # Check if a layout already exists for this venue + pageant combo
    existing = (
        db.query(VenueLayout)
        .filter(
            VenueLayout.venue_id == payload.venue_id,
            VenueLayout.pageant_id == pageant_id,
        )
        .first()
    )

    if existing:
        # Update existing layout
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    # Create new layout
    layout = VenueLayout(pageant_id=pageant_id, **payload.model_dump())
    db.add(layout)
    db.commit()
    db.refresh(layout)
    return layout