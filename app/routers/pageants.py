"""Router for pageant CRUD, branding, age divisions, categories, and scoring rubrics."""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models
from app import schemas

router = APIRouter(prefix="/pageants", tags=["pageants"])


def _tenant_id(x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID")) -> int:
    """Extract tenant ID from header, defaulting to 1."""
    return x_tenant_id or 1


# ── Pageant CRUD ────────────────────────────────────────────────────────


@router.get("/", response_model=list[schemas.PageantOut])
def list_pageants(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
    skip: int = 0,
    limit: int = 100,
):
    """List all pageants belonging to the current tenant."""
    return (
        db.query(models.Pageant)
        .filter(models.Pageant.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=schemas.PageantOut, status_code=201)
def create_pageant(
    payload: schemas.PageantCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create a new pageant for the current tenant."""
    # Verify tenant exists
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Check slug uniqueness
    existing = db.query(models.Pageant).filter(models.Pageant.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="A pageant with this slug already exists")

    pageant = models.Pageant(**payload.model_dump(), tenant_id=tenant_id)
    db.add(pageant)
    db.commit()
    db.refresh(pageant)
    return pageant


@router.get("/{pageant_id}", response_model=schemas.PageantOut)
def get_pageant(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Get a single pageant by ID (scoped to tenant)."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")
    return pageant


@router.patch("/{pageant_id}", response_model=schemas.PageantOut)
def update_pageant(
    pageant_id: int,
    payload: schemas.PageantUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Update an existing pageant (partial update)."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pageant, field, value)
    db.commit()
    db.refresh(pageant)
    return pageant


# ── Branding ────────────────────────────────────────────────────────────


@router.get("/{pageant_id}/branding", response_model=schemas.PageantBrandingOut)
def get_branding(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Get the branding record for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")
    if not pageant.branding:
        raise HTTPException(status_code=404, detail="Branding not found for this pageant")
    return pageant.branding


@router.put("/{pageant_id}/branding", response_model=schemas.PageantBrandingOut)
def update_branding(
    pageant_id: int,
    payload: schemas.PageantBrandingUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create or update the branding record for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    if pageant.branding:
        # Update existing
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pageant.branding, field, value)
    else:
        # Create new
        branding = models.PageantBranding(**payload.model_dump(exclude_unset=True), pageant_id=pageant_id)
        db.add(branding)

    db.commit()
    db.refresh(pageant)
    # pageant.branding is refreshed via the relationship
    return pageant.branding


# ── Age Divisions ───────────────────────────────────────────────────────


@router.get("/{pageant_id}/divisions", response_model=list[schemas.AgeDivisionOut])
def list_divisions(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """List all age divisions for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")
    return pageant.age_divisions


@router.post("/{pageant_id}/divisions", response_model=schemas.AgeDivisionOut, status_code=201)
def create_division(
    pageant_id: int,
    payload: schemas.AgeDivisionCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create a new age division for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = models.AgeDivision(**payload.model_dump(), pageant_id=pageant_id)
    db.add(division)
    db.commit()
    db.refresh(division)
    return division


# ── Competition Categories ──────────────────────────────────────────────


@router.get(
    "/{pageant_id}/divisions/{div_id}/categories",
    response_model=list[schemas.CompetitionCategoryOut],
)
def list_categories(
    pageant_id: int,
    div_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """List all competition categories for a given age division."""
    # Verify pageant + division belong to tenant
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = (
        db.query(models.AgeDivision)
        .filter(models.AgeDivision.id == div_id, models.AgeDivision.pageant_id == pageant_id)
        .first()
    )
    if not division:
        raise HTTPException(status_code=404, detail="Age division not found")

    return division.categories


@router.post(
    "/{pageant_id}/divisions/{div_id}/categories",
    response_model=schemas.CompetitionCategoryOut,
    status_code=201,
)
def create_category(
    pageant_id: int,
    div_id: int,
    payload: schemas.CompetitionCategoryCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create a new competition category under an age division."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = (
        db.query(models.AgeDivision)
        .filter(models.AgeDivision.id == div_id, models.AgeDivision.pageant_id == pageant_id)
        .first()
    )
    if not division:
        raise HTTPException(status_code=404, detail="Age division not found")

    category = models.CompetitionCategory(**payload.model_dump(), division_id=div_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ── Scoring Rubric ──────────────────────────────────────────────────────


@router.get(
    "/{pageant_id}/divisions/{div_id}/categories/{cat_id}/rubric",
    response_model=schemas.ScoringRubricOut,
)
def get_rubric(
    pageant_id: int,
    div_id: int,
    cat_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Get the scoring rubric for a specific competition category."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = (
        db.query(models.AgeDivision)
        .filter(models.AgeDivision.id == div_id, models.AgeDivision.pageant_id == pageant_id)
        .first()
    )
    if not division:
        raise HTTPException(status_code=404, detail="Age division not found")

    category = (
        db.query(models.CompetitionCategory)
        .filter(
            models.CompetitionCategory.id == cat_id,
            models.CompetitionCategory.division_id == div_id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Competition category not found")
    if not category.scoring_rubric:
        raise HTTPException(status_code=404, detail="Scoring rubric not found for this category")

    return category.scoring_rubric


@router.put(
    "/{pageant_id}/divisions/{div_id}/categories/{cat_id}/rubric",
    response_model=schemas.ScoringRubricOut,
)
def create_or_update_rubric(
    pageant_id: int,
    div_id: int,
    cat_id: int,
    payload: schemas.ScoringRubricCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create or update the scoring rubric for a competition category."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = (
        db.query(models.AgeDivision)
        .filter(models.AgeDivision.id == div_id, models.AgeDivision.pageant_id == pageant_id)
        .first()
    )
    if not division:
        raise HTTPException(status_code=404, detail="Age division not found")

    category = (
        db.query(models.CompetitionCategory)
        .filter(
            models.CompetitionCategory.id == cat_id,
            models.CompetitionCategory.division_id == div_id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Competition category not found")

    if category.scoring_rubric:
        # Update existing
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category.scoring_rubric, field, value)
        db.commit()
        db.refresh(category.scoring_rubric)
        return category.scoring_rubric

    # Create new
    rubric = models.ScoringRubric(**payload.model_dump(), category_id=cat_id)
    db.add(rubric)
    db.commit()
    db.refresh(rubric)
    return rubric