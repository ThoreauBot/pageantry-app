"""Marketing, social media, program book, and ad endpoints for the Pageantry Application."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import (
    Pageant,
    MarketingCampaign,
    SocialMediaPost,
    ProgramBook,
    Ad,
)
from app.schemas import (
    MarketingCampaignCreate,
    MarketingCampaignUpdate,
    MarketingCampaignOut,
    SocialMediaPostCreate,
    SocialMediaPostUpdate,
    SocialMediaPostOut,
    ProgramBookCreate,
    ProgramBookOut,
    AdCreate,
    AdOut,
)

router = APIRouter(tags=["marketing"])


# ── Marketing Campaigns ─────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/campaigns",
    response_model=List[MarketingCampaignOut],
)
def list_marketing_campaigns(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List marketing campaigns for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    campaigns = (
        db.query(MarketingCampaign)
        .filter(MarketingCampaign.pageant_id == pageant_id)
        .all()
    )
    return campaigns


@router.post(
    "/pageants/{pageant_id}/campaigns",
    response_model=MarketingCampaignOut,
    status_code=status.HTTP_201_CREATED,
)
def create_marketing_campaign(
    pageant_id: int,
    payload: MarketingCampaignCreate,
    db: Session = Depends(get_db),
):
    """Create a marketing campaign for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    campaign = MarketingCampaign(
        pageant_id=pageant_id, **payload.model_dump()
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.patch(
    "/campaigns/{campaign_id}",
    response_model=MarketingCampaignOut,
)
def update_marketing_campaign(
    campaign_id: int,
    payload: MarketingCampaignUpdate,
    db: Session = Depends(get_db),
):
    """Update a marketing campaign."""
    campaign = (
        db.query(MarketingCampaign)
        .filter(MarketingCampaign.id == campaign_id)
        .first()
    )
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketing campaign not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return campaign


# ── Social Media Posts ──────────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/posts",
    response_model=SocialMediaPostOut,
    status_code=status.HTTP_201_CREATED,
)
def create_social_media_post(
    pageant_id: int,
    payload: SocialMediaPostCreate,
    db: Session = Depends(get_db),
):
    """Create a social media post for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    post = SocialMediaPost(
        pageant_id=pageant_id, **payload.model_dump()
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get(
    "/pageants/{pageant_id}/posts",
    response_model=List[SocialMediaPostOut],
)
def list_social_media_posts(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List social media posts for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    posts = (
        db.query(SocialMediaPost)
        .filter(SocialMediaPost.pageant_id == pageant_id)
        .all()
    )
    return posts


@router.patch(
    "/posts/{post_id}",
    response_model=SocialMediaPostOut,
)
def update_post_status(
    post_id: int,
    payload: SocialMediaPostUpdate,
    db: Session = Depends(get_db),
):
    """Update a social media post (status, content, etc.)."""
    post = (
        db.query(SocialMediaPost)
        .filter(SocialMediaPost.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social media post not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


# ── Program Book ────────────────────────────────────────────────────────


@router.get(
    "/pageants/{pageant_id}/program-book",
    response_model=ProgramBookOut,
)
def get_program_book(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """Get the program book for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    book = (
        db.query(ProgramBook)
        .filter(ProgramBook.pageant_id == pageant_id)
        .first()
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program book not found",
        )
    return book


@router.post(
    "/pageants/{pageant_id}/program-book",
    response_model=ProgramBookOut,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_program_book(
    pageant_id: int,
    payload: ProgramBookCreate,
    db: Session = Depends(get_db),
):
    """Create or update the program book for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )

    existing = (
        db.query(ProgramBook)
        .filter(ProgramBook.pageant_id == pageant_id)
        .first()
    )

    if existing:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    book = ProgramBook(pageant_id=pageant_id, **payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


# ── Ads ─────────────────────────────────────────────────────────────────


@router.post(
    "/pageants/{pageant_id}/ads",
    response_model=AdOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ad(
    pageant_id: int,
    payload: AdCreate,
    db: Session = Depends(get_db),
):
    """Create an ad for a pageant's program book."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    # Auto-resolve the program book for this pageant
    book = db.query(ProgramBook).filter(ProgramBook.pageant_id == pageant_id).first()
    if not book:
        # Create a default program book if none exists
        book = ProgramBook(pageant_id=pageant_id)
        db.add(book)
        db.flush()
    ad = Ad(pageant_id=pageant_id, program_book_id=book.id, **payload.model_dump())
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


@router.get(
    "/pageants/{pageant_id}/ads",
    response_model=List[AdOut],
)
def list_ads(
    pageant_id: int,
    db: Session = Depends(get_db),
):
    """List ads for a pageant."""
    pageant = db.query(Pageant).filter(Pageant.id == pageant_id).first()
    if not pageant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pageant not found",
        )
    ads = (
        db.query(Ad)
        .filter(Ad.pageant_id == pageant_id)
        .all()
    )
    return ads