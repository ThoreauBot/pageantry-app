"""Pydantic schemas for the Pageantry Application."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Tenant / Auth ──────────────────────────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "director"

class TenantLogin(BaseModel):
    email: str
    password: str

class TenantOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Pageant ────────────────────────────────────────────────────────────

class PageantCreate(BaseModel):
    name: str
    mission_statement: Optional[str] = None
    slug: str
    pageant_type: str = "representative"
    business_structure: Optional[str] = None

class PageantUpdate(BaseModel):
    name: Optional[str] = None
    mission_statement: Optional[str] = None
    status: Optional[str] = None
    pageant_type: Optional[str] = None
    business_structure: Optional[str] = None

class PageantOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    mission_statement: Optional[str]
    slug: str
    pageant_type: str
    status: str
    business_structure: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageantBrandingUpdate(BaseModel):
    logo_url: Optional[str] = None
    color_palette: Optional[dict] = None
    slogan: Optional[str] = None
    font_preferences: Optional[str] = None

class PageantBrandingOut(BaseModel):
    id: int
    pageant_id: int
    logo_url: Optional[str]
    color_palette: Optional[dict]
    slogan: Optional[str]
    font_preferences: Optional[str]

    class Config:
        from_attributes = True


# ── Age Divisions ──────────────────────────────────────────────────────

class AgeDivisionCreate(BaseModel):
    name: str
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    eligibility_rules: Optional[str] = None
    sort_order: int = 0

class AgeDivisionOut(BaseModel):
    id: int
    pageant_id: int
    name: str
    min_age: Optional[int]
    max_age: Optional[int]
    gender: Optional[str]
    eligibility_rules: Optional[str]
    sort_order: int

    class Config:
        from_attributes = True


class CompetitionCategoryCreate(BaseModel):
    name: str
    category_type: str = "on_stage"
    sort_order: int = 0
    scoring_weight: float = 1.0
    time_limit_seconds: Optional[int] = None
    attire_guidelines: Optional[str] = None

class CompetitionCategoryOut(BaseModel):
    id: int
    division_id: int
    name: str
    category_type: str
    sort_order: int
    scoring_weight: float
    time_limit_seconds: Optional[int]
    attire_guidelines: Optional[str]

    class Config:
        from_attributes = True


# ── Scoring ────────────────────────────────────────────────────────────

class ScoringRubricCreate(BaseModel):
    name: str
    max_score: float = 10.0
    allow_half_points: bool = True
    criteria_text: Optional[str] = None

class ScoringRubricOut(BaseModel):
    id: int
    category_id: int
    name: str
    max_score: float
    allow_half_points: bool
    criteria_text: Optional[str]

    class Config:
        from_attributes = True


class JudgeCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_head_judge: bool = False
    is_backup: bool = False
    notes: Optional[str] = None

class JudgeOut(BaseModel):
    id: int
    panel_id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    is_head_judge: bool
    is_backup: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


class JudgePanelCreate(BaseModel):
    name: Optional[str] = None
    head_judge_id: Optional[int] = None

class JudgePanelOut(BaseModel):
    id: int
    pageant_id: int
    name: Optional[str]
    head_judge_id: Optional[int]
    orientation_date: Optional[datetime]
    judges: List[JudgeOut] = []

    class Config:
        from_attributes = True


# ── Contestant ─────────────────────────────────────────────────────────

class ContestantCreate(BaseModel):
    division_id: int
    first_name: str
    last_name: str
    age: Optional[int] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    platform_statement: Optional[str] = None
    bio: Optional[str] = None

class ContestantOut(BaseModel):
    id: int
    pageant_id: int
    division_id: Optional[int]
    contestant_number: Optional[int]
    first_name: str
    last_name: str
    age: Optional[int]
    email: Optional[str]
    status: str
    checked_in_at: Optional[datetime]
    registered_at: datetime

    class Config:
        from_attributes = True


class ContestantDetail(BaseModel):
    """Full contestant detail including documents and fees."""
    id: int
    pageant_id: int
    division_id: Optional[int]
    contestant_number: Optional[int]
    first_name: str
    last_name: str
    age: Optional[int]
    birthdate: Optional[date]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    emergency_contact: Optional[str]
    photo_url: Optional[str]
    status: str
    platform_statement: Optional[str]
    bio: Optional[str]
    dressing_area: Optional[str]
    registered_at: datetime
    checked_in_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Score Entry ────────────────────────────────────────────────────────

class ScoreEntryCreate(BaseModel):
    contestant_id: int
    judge_id: int
    category_id: int
    score_value: float = Field(ge=0, le=10)
    comment: Optional[str] = None
    division_id: Optional[int] = None
    is_synced: bool = True

class ScoreEntryOut(BaseModel):
    id: int
    pageant_id: int
    contestant_id: int
    judge_id: int
    category_id: int
    score_value: float
    comment: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class TabulationResult(BaseModel):
    contestant_id: int
    contestant_name: str
    division_id: Optional[int]
    rank: Optional[int]
    total_score: Optional[float]
    is_winner: bool
    is_runner_up: bool
    side_awards: Optional[dict]


# ── Venue ──────────────────────────────────────────────────────────────

class VenueCreate(BaseModel):
    name: str
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    capacity: Optional[int] = None
    stage_dimensions: Optional[str] = None
    has_built_in_stage: bool = False
    parking_info: Optional[str] = None
    accessibility_notes: Optional[str] = None

class VenueOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    contact_name: Optional[str]
    capacity: Optional[int]
    stage_dimensions: Optional[str]
    has_built_in_stage: bool

    class Config:
        from_attributes = True


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    capacity: Optional[int] = None
    stage_dimensions: Optional[str] = None
    has_built_in_stage: Optional[bool] = None
    parking_info: Optional[str] = None
    accessibility_notes: Optional[str] = None


class VenueAmenityCreate(BaseModel):
    amenity_type: str
    included_in_rental: bool = True
    cost_if_not_included: Optional[float] = None


class VenueAmenityOut(BaseModel):
    id: int
    venue_id: int
    amenity_type: str
    included_in_rental: bool
    cost_if_not_included: Optional[float]

    class Config:
        from_attributes = True


class VenueContractCreate(BaseModel):
    venue_id: int
    rental_cost: Optional[float] = None
    deposit_amount: float = 0.0
    deposit_due_date: Optional[date] = None
    balance_due_date: Optional[date] = None
    status: str = "draft"

class VenueContractUpdate(BaseModel):
    venue_id: Optional[int] = None
    rental_cost: Optional[float] = None
    deposit_amount: Optional[float] = None
    deposit_due_date: Optional[date] = None
    balance_due_date: Optional[date] = None
    insurance_requirements: Optional[str] = None
    cancellation_terms: Optional[str] = None
    file_url: Optional[str] = None
    status: Optional[str] = None


class VenueLayoutCreate(BaseModel):
    venue_id: int
    stage_formation: str = "diamond"
    registration_table_location: Optional[str] = None
    dressing_area_location: Optional[str] = None
    judges_table_location: Optional[str] = None
    seating_capacity_used: Optional[int] = None


class VenueLayoutOut(BaseModel):
    id: int
    venue_id: int
    pageant_id: int
    stage_formation: str
    registration_table_location: Optional[str]
    dressing_area_location: Optional[str]
    judges_table_location: Optional[str]
    seating_capacity_used: Optional[int]

    class Config:
        from_attributes = True


class VenueContractOut(BaseModel):
    id: int
    venue_id: int
    pageant_id: int
    rental_cost: Optional[float]
    deposit_amount: float
    status: str

    class Config:
        from_attributes = True


# ── Sponsor / Donor ────────────────────────────────────────────────────

class SponsorCreate(BaseModel):
    business_name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

class SponsorUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None


class SponsorOut(BaseModel):
    id: int
    pageant_id: int
    business_name: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    website: Optional[str]

    class Config:
        from_attributes = True


class SponsorshipTierCreate(BaseModel):
    name: str
    minimum_amount: Optional[float] = None
    benefits_description: Optional[str] = None

class SponsorshipTierOut(BaseModel):
    id: int
    pageant_id: int
    name: str
    minimum_amount: Optional[float]
    benefits_description: Optional[str]

    class Config:
        from_attributes = True


class SponsorshipAgreementCreate(BaseModel):
    sponsor_id: int
    tier_id: Optional[int] = None
    amount: Optional[float] = None
    in_kind_value: float = 0.0
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SponsorshipAgreementOut(BaseModel):
    id: int
    sponsor_id: int
    tier_id: Optional[int]
    amount: Optional[float]
    in_kind_value: float
    status: str

    class Config:
        from_attributes = True


class DonationCreate(BaseModel):
    donor_name: str
    donor_type: str = "individual"
    amount: Optional[float] = None
    in_kind_description: Optional[str] = None

class DonationOut(BaseModel):
    id: int
    pageant_id: int
    donor_name: str
    donor_type: str
    amount: Optional[float]
    in_kind_description: Optional[str]
    donation_date: datetime

    class Config:
        from_attributes = True


class BarterAgreementCreate(BaseModel):
    partner_name: str
    service_provided: Optional[str] = None
    promotion_provided_in_exchange: Optional[str] = None
    value_estimate: Optional[float] = None
    written_agreement_url: Optional[str] = None


class BarterAgreementOut(BaseModel):
    id: int
    pageant_id: int
    partner_name: str
    service_provided: Optional[str]
    promotion_provided_in_exchange: Optional[str]
    value_estimate: Optional[float]
    written_agreement_url: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ── Marketing ──────────────────────────────────────────────────────────

class MarketingCampaignCreate(BaseModel):
    name: str
    campaign_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None

class MarketingCampaignUpdate(BaseModel):
    name: Optional[str] = None
    campaign_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    status: Optional[str] = None


class MarketingCampaignOut(BaseModel):
    id: int
    pageant_id: int
    name: str
    campaign_type: str
    start_date: Optional[date]
    end_date: Optional[date]
    status: str

    class Config:
        from_attributes = True


class SocialMediaPostCreate(BaseModel):
    platform: str
    content: Optional[str] = None
    media_urls: Optional[list] = None
    scheduled_date: Optional[datetime] = None

class SocialMediaPostUpdate(BaseModel):
    platform: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[list] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None


class SocialMediaPostOut(BaseModel):
    id: int
    pageant_id: int
    platform: str
    content: Optional[str]
    scheduled_date: Optional[datetime]
    status: str

    class Config:
        from_attributes = True


# ── Program Book ───────────────────────────────────────────────────────

class ProgramBookCreate(BaseModel):
    format: str = "printed_and_digital"
    print_run_count: Optional[int] = None
    distribution_strategy: str = "every_contestant"

class ProgramBookOut(BaseModel):
    id: int
    pageant_id: int
    format: str
    print_run_count: Optional[int]
    distribution_strategy: str

    class Config:
        from_attributes = True


class AdCreate(BaseModel):
    advertiser_name: str
    advertiser_type: str
    ad_size: str
    fee: float = 0.0

class AdOut(BaseModel):
    id: int
    pageant_id: int
    advertiser_name: str
    advertiser_type: str
    ad_size: str
    status: str
    fee: float
    paid: bool

    class Config:
        from_attributes = True


# ── Titleholder ────────────────────────────────────────────────────────

class TitleholderCreate(BaseModel):
    contestant_id: int
    title: Optional[str] = None
    reign_start_date: date
    reign_end_date: Optional[date] = None

class TitleholderOut(BaseModel):
    id: int
    contestant_id: int
    title: Optional[str]
    reign_start_date: date
    reign_end_date: Optional[date]
    status: str

    class Config:
        from_attributes = True


class AppearanceCreate(BaseModel):
    event_name: str
    date: date
    location: Optional[str] = None
    appearance_type: Optional[str] = None
    notes: Optional[str] = None
    hours_logged: Optional[float] = None

class AppearanceOut(BaseModel):
    id: int
    titleholder_id: int
    event_name: str
    date: date
    location: Optional[str]
    appearance_type: Optional[str]
    hours_logged: Optional[float]

    class Config:
        from_attributes = True


# ── Financial ──────────────────────────────────────────────────────────

class BudgetLineItemCreate(BaseModel):
    category: str
    description: str
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    vendor_name: Optional[str] = None

class BudgetLineItemOut(BaseModel):
    id: int
    pageant_id: int
    category: str
    description: str
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    vendor_name: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ── Dashboard ──────────────────────────────────────────────────────────

# ── Missing schemas used by routers ─────────────────────────────────

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    capacity: Optional[int] = None
    stage_dimensions: Optional[str] = None
    has_built_in_stage: Optional[bool] = None
    parking_info: Optional[str] = None
    accessibility_notes: Optional[str] = None

class VenueAmenityCreate(BaseModel):
    amenity_type: str
    included_in_rental: bool = True
    cost_if_not_included: Optional[float] = None

class VenueAmenityOut(BaseModel):
    id: int
    venue_id: int
    amenity_type: str
    included_in_rental: bool
    cost_if_not_included: Optional[float]

    class Config:
        from_attributes = True

class VenueContractUpdate(BaseModel):
    rental_cost: Optional[float] = None
    deposit_amount: Optional[float] = None
    status: Optional[str] = None

class VenueLayoutCreate(BaseModel):
    venue_id: int
    stage_formation: str = "diamond"
    registration_table_location: Optional[str] = None
    dressing_area_location: Optional[str] = None
    judges_table_location: Optional[str] = None
    seating_capacity_used: Optional[int] = None

class VenueLayoutOut(BaseModel):
    id: int
    venue_id: int
    pageant_id: int
    stage_formation: str
    seating_capacity_used: Optional[int]

    class Config:
        from_attributes = True

class SponsorUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

class BarterAgreementCreate(BaseModel):
    partner_name: str
    service_provided: Optional[str] = None
    promotion_provided_in_exchange: Optional[str] = None
    value_estimate: Optional[float] = None

class BarterAgreementOut(BaseModel):
    id: int
    pageant_id: int
    partner_name: str
    service_provided: Optional[str]
    value_estimate: Optional[float]
    status: str

    class Config:
        from_attributes = True

class MarketingCampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None

class SocialMediaPostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None

class JudgePanelCreatePanel(BaseModel):
    """Schema for creating a panel with inline judges."""
    name: Optional[str] = None
    judges: list = []

class DashboardStats(BaseModel):
    total_contestants: int = 0
    checked_in: int = 0
    total_sponsors: int = 0
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    registered_contestants: int = 0
    pageant_status: str = "draft"
    upcoming_events: List[dict] = []