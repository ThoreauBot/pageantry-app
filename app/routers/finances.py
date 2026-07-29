"""Finances router: budget line items and financial summaries."""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BudgetLineItem, BudgetStatus, Donation, SponsorshipTier
from app.schemas import BudgetLineItemCreate, BudgetLineItemOut

router = APIRouter(tags=["finances"])


# ── Additional schemas ──────────────────────────────────────────────

class BudgetLineItemUpdate(BaseModel):
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    vendor_name: Optional[str] = None
    status: Optional[str] = None


class FinancialSummary(BaseModel):
    pageant_id: int
    total_budgeted: float
    total_actual_expenses: float
    total_sponsorship_revenue: float
    total_donations: float
    total_revenue: float
    net: float


# ── Budget Line Items ───────────────────────────────────────────────

@router.get(
    "/pageants/{pageant_id}/budget",
    response_model=List[BudgetLineItemOut],
)
def list_budget(pageant_id: int, db: Session = Depends(get_db)):
    """List all budget line items for a pageant."""
    items = (
        db.query(BudgetLineItem)
        .filter(BudgetLineItem.pageant_id == pageant_id)
        .order_by(BudgetLineItem.category)
        .all()
    )
    return items


@router.post(
    "/pageants/{pageant_id}/budget",
    response_model=BudgetLineItemOut,
    status_code=201,
)
def create_budget_item(
    pageant_id: int,
    payload: BudgetLineItemCreate,
    db: Session = Depends(get_db),
):
    """Create a new budget line item for a pageant."""
    item = BudgetLineItem(
        pageant_id=pageant_id,
        category=payload.category,
        description=payload.description,
        estimated_cost=payload.estimated_cost,
        actual_cost=payload.actual_cost,
        vendor_name=payload.vendor_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/budget/{item_id}", response_model=BudgetLineItemOut)
def update_budget_item(
    item_id: int,
    payload: BudgetLineItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a budget line item (actual costs, vendor, status)."""
    item = db.query(BudgetLineItem).filter(BudgetLineItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Budget line item not found")

    if payload.estimated_cost is not None:
        item.estimated_cost = payload.estimated_cost
    if payload.actual_cost is not None:
        item.actual_cost = payload.actual_cost
    if payload.vendor_name is not None:
        item.vendor_name = payload.vendor_name
    if payload.status is not None:
        valid_statuses = {s.value for s in BudgetStatus}
        if payload.status not in valid_statuses:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}",
            )
        item.status = payload.status

    db.commit()
    db.refresh(item)
    return item


# ── Financial Summary ───────────────────────────────────────────────

@router.get(
    "/pageants/{pageant_id}/financial-summary",
    response_model=FinancialSummary,
)
def financial_summary(pageant_id: int, db: Session = Depends(get_db)):
    """Get revenue vs expenses summary for a pageant."""
    # Budgeted totals
    budgeted = (
        db.query(func.coalesce(func.sum(BudgetLineItem.estimated_cost), 0.0))
        .filter(BudgetLineItem.pageant_id == pageant_id)
        .scalar()
    )
    actual_expenses = (
        db.query(func.coalesce(func.sum(BudgetLineItem.actual_cost), 0.0))
        .filter(BudgetLineItem.pageant_id == pageant_id)
        .scalar()
    )

    # Sponsorship revenue: sum of amounts from sponsorship_agreements via tiers
    sponsorship_revenue = (
        db.query(func.coalesce(func.sum(SponsorshipTier.minimum_amount), 0.0))
        .filter(SponsorshipTier.pageant_id == pageant_id)
        .scalar()
    )

    # Donations
    donations = (
        db.query(func.coalesce(func.sum(Donation.amount), 0.0))
        .filter(
            Donation.pageant_id == pageant_id,
            Donation.amount.isnot(None),
        )
        .scalar()
    )

    total_revenue = sponsorship_revenue + donations
    net = total_revenue - actual_expenses

    return FinancialSummary(
        pageant_id=pageant_id,
        total_budgeted=budgeted,
        total_actual_expenses=actual_expenses,
        total_sponsorship_revenue=sponsorship_revenue,
        total_donations=donations,
        total_revenue=total_revenue,
        net=net,
    )