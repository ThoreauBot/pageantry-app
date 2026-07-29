"""SQLAlchemy models for the Pageantry Application."""
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text, JSON, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ── Enums ──────────────────────────────────────────────────────────────

class PageantType(str, enum.Enum):
    representative = "representative"
    hobby = "hobby"

class PageantStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"

class BusinessStructure(str, enum.Enum):
    sole_proprietor = "sole_proprietor"
    llc = "llc"
    corporation = "corporation"
    nonprofit = "nonprofit"

class ContestantStatus(str, enum.Enum):
    registered = "registered"
    checked_in = "checked_in"
    competed = "competed"
    no_show = "no_show"

class FeeStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    refunded = "refunded"

class TitleholderStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    removed = "removed"
    resigned = "resigned"

class AgreementStatus(str, enum.Enum):
    active = "active"
    fulfilled = "fulfilled"
    expired = "expired"

class CampaignStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"

class PostStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"

class AppearanceStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    completed = "completed"

class BudgetStatus(str, enum.Enum):
    budgeted = "budgeted"
    ordered = "ordered"
    paid = "paid"

class SideEventType(str, enum.Enum):
    photogenic = "photogenic"
    crowd_favorite = "crowd_favorite"
    peoples_choice = "peoples_choice"
    community_service = "community_service"
    academic = "academic"
    talent = "talent"
    other = "other"

class CategoryType(str, enum.Enum):
    on_stage = "on_stage"
    off_stage = "off_stage"
    optional = "optional"

class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"

class TenantRole(str, enum.Enum):
    director = "director"
    assistant_director = "assistant_director"
    tabulator = "tabulator"
    judge = "judge"
    contestant = "contestant"
    sponsor = "sponsor"
    super_admin = "super_admin"


# ── Tenant / Auth ──────────────────────────────────────────────────────

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # None for SSO
    role = Column(SAEnum(TenantRole), default=TenantRole.director)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pageants = relationship("Pageant", back_populates="tenant")
    judge_panels = relationship("JudgePanel", back_populates="tenant")


# ── Pageant ────────────────────────────────────────────────────────────

class Pageant(Base):
    __tablename__ = "pageants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    mission_statement = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False)
    pageant_type = Column(SAEnum(PageantType), default=PageantType.representative)
    status = Column(SAEnum(PageantStatus), default=PageantStatus.draft)
    business_structure = Column(SAEnum(BusinessStructure), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="pageants")
    branding = relationship("PageantBranding", uselist=False, back_populates="pageant")
    settings = relationship("PageantSetting", back_populates="pageant")
    age_divisions = relationship("AgeDivision", back_populates="pageant")
    side_events = relationship("SideEvent", back_populates="pageant")
    judge_panels_via = relationship("JudgePanel", back_populates="pageant")
    scoring_scales = relationship("ScoringScale", back_populates="pageant")
    tie_break_rules = relationship("TieBreakRule", back_populates="pageant")
    venues = relationship("VenueContract", back_populates="pageant")
    venue_layouts = relationship("VenueLayout", back_populates="pageant")
    schedule = relationship("PageantSchedule", uselist=False, back_populates="pageant")
    rehearsals = relationship("Rehearsal", back_populates="pageant")
    contestants = relationship("Contestant", back_populates="pageant")
    sponsors = relationship("Sponsor", back_populates="pageant")
    sponsorship_tiers = relationship("SponsorshipTier", back_populates="pageant")
    donations = relationship("Donation", back_populates="pageant")
    barter_agreements = relationship("BarterAgreement", back_populates="pageant")
    program_book = relationship("ProgramBook", uselist=False, back_populates="pageant")
    ads = relationship("Ad", back_populates="pageant")
    marketing_campaigns = relationship("MarketingCampaign", back_populates="pageant")
    score_entries = relationship("ScoreEntry", back_populates="pageant")
    tabulation_runs = relationship("TabulationRun", back_populates="pageant")
    budget_line_items = relationship("BudgetLineItem", back_populates="pageant")


class PageantBranding(Base):
    __tablename__ = "pageant_branding"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False, unique=True)
    logo_url = Column(String(500), nullable=True)
    color_palette = Column(JSON, nullable=True)
    slogan = Column(String(255), nullable=True)
    font_preferences = Column(String(255), nullable=True)

    pageant = relationship("Pageant", back_populates="branding")


class PageantSetting(Base):
    __tablename__ = "pageant_settings"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)

    pageant = relationship("Pageant", back_populates="settings")


# ── Age Divisions & Categories ─────────────────────────────────────────

class AgeDivision(Base):
    __tablename__ = "age_divisions"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    age_as_of_date = Column(Date, nullable=True)
    eligibility_rules = Column(Text, nullable=True)
    eligibility_residency = Column(String(255), nullable=True)
    eligibility_marital_status = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)

    pageant = relationship("Pageant", back_populates="age_divisions")
    categories = relationship("CompetitionCategory", back_populates="age_division")


class CompetitionCategory(Base):
    __tablename__ = "competition_categories"

    id = Column(Integer, primary_key=True, index=True)
    division_id = Column(Integer, ForeignKey("age_divisions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category_type = Column(SAEnum(CategoryType), default=CategoryType.on_stage)
    sort_order = Column(Integer, default=0)
    scoring_weight = Column(Float, default=1.0)
    time_limit_seconds = Column(Integer, nullable=True)
    attire_guidelines = Column(Text, nullable=True)
    music_required = Column(Boolean, default=False)

    age_division = relationship("AgeDivision", back_populates="categories")
    scoring_rubric = relationship("ScoringRubric", uselist=False, back_populates="category")
    score_entries = relationship("ScoreEntry", back_populates="category")


class SideEvent(Base):
    __tablename__ = "side_events"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    event_type = Column(SAEnum(SideEventType), default=SideEventType.other)
    fee = Column(Float, default=0.0)
    is_optional = Column(Boolean, default=True)
    is_fundraiser = Column(Boolean, default=False)

    pageant = relationship("Pageant", back_populates="side_events")


# ── Scoring ────────────────────────────────────────────────────────────

class ScoringRubric(Base):
    __tablename__ = "scoring_rubrics"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("competition_categories.id"), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    max_score = Column(Float, default=10.0)
    allow_half_points = Column(Boolean, default=True)
    criteria_text = Column(Text, nullable=True)

    category = relationship("CompetitionCategory", back_populates="scoring_rubric")


class ScoringScale(Base):
    __tablename__ = "scoring_scales"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    min_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    label = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    pageant = relationship("Pageant", back_populates="scoring_scales")


class TieBreakRule(Base):
    __tablename__ = "tie_break_rules"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    method = Column(String(50), nullable=False)  # head_judge_decides, re_score, highest_category, etc.
    category_id = Column(Integer, ForeignKey("competition_categories.id"), nullable=True)
    description = Column(Text, nullable=True)

    pageant = relationship("Pageant", back_populates="tie_break_rules")


class JudgePanel(Base):
    __tablename__ = "judge_panels"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    name = Column(String(100), nullable=True)
    head_judge_id = Column(Integer, nullable=True)
    backup_judge_id = Column(Integer, nullable=True)
    orientation_date = Column(DateTime, nullable=True)

    pageant = relationship("Pageant", back_populates="judge_panels_via")
    tenant = relationship("Tenant", back_populates="judge_panels")
    judges = relationship("Judge", back_populates="panel")


class Judge(Base):
    __tablename__ = "judges"

    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(Integer, ForeignKey("judge_panels.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    is_head_judge = Column(Boolean, default=False)
    is_backup = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    panel = relationship("JudgePanel", back_populates="judges")
    score_entries = relationship("ScoreEntry", back_populates="judge")


# ── Scheduling ─────────────────────────────────────────────────────────

class PageantSchedule(Base):
    __tablename__ = "pageant_schedules"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False, unique=True)
    pageant_date = Column(Date, nullable=False)
    doors_open_time = Column(String(10), nullable=True)
    start_time = Column(String(10), nullable=False)
    estimated_end_time = Column(String(10), nullable=True)
    day_of_week = Column(SAEnum(DayOfWeek), nullable=True)
    timezone = Column(String(50), default="America/Chicago")
    conflict_radius_miles = Column(Integer, default=120)

    pageant = relationship("Pageant", back_populates="schedule")


class Rehearsal(Base):
    __tablename__ = "rehearsals"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=True)
    location = Column(String(255), nullable=True)
    mandatory = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    pageant = relationship("Pageant", back_populates="rehearsals")


# ── Venue ──────────────────────────────────────────────────────────────

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=True)
    stage_dimensions = Column(String(100), nullable=True)
    has_built_in_stage = Column(Boolean, default=False)
    parking_info = Column(Text, nullable=True)
    accessibility_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contracts = relationship("VenueContract", back_populates="venue")
    amenities = relationship("VenueAmenity", back_populates="venue")


class VenueContract(Base):
    __tablename__ = "venue_contracts"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    rental_cost = Column(Float, nullable=True)
    deposit_amount = Column(Float, default=0.0)
    deposit_due_date = Column(Date, nullable=True)
    balance_due_date = Column(Date, nullable=True)
    insurance_requirements = Column(Text, nullable=True)
    cancellation_terms = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")

    venue = relationship("Venue", back_populates="contracts")
    pageant = relationship("Pageant", back_populates="venues")


class VenueAmenity(Base):
    __tablename__ = "venue_amenities"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    amenity_type = Column(String(50), nullable=False)
    included_in_rental = Column(Boolean, default=True)
    cost_if_not_included = Column(Float, nullable=True)

    venue = relationship("Venue", back_populates="amenities")


class VenueLayout(Base):
    __tablename__ = "venue_layouts"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    stage_formation = Column(String(50), default="diamond")
    registration_table_location = Column(String(255), nullable=True)
    dressing_area_location = Column(String(255), nullable=True)
    judges_table_location = Column(String(255), nullable=True)
    seating_capacity_used = Column(Integer, nullable=True)

    pageant = relationship("Pageant", back_populates="venue_layouts")


# ── Contestant ─────────────────────────────────────────────────────────

class Contestant(Base):
    __tablename__ = "contestants"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    division_id = Column(Integer, ForeignKey("age_divisions.id"), nullable=True)
    contestant_number = Column(Integer, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    birthdate = Column(Date, nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    status = Column(SAEnum(ContestantStatus), default=ContestantStatus.registered)
    platform_statement = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    checked_in_at = Column(DateTime, nullable=True)
    dressing_area = Column(String(100), nullable=True)

    pageant = relationship("Pageant", back_populates="contestants")
    documents = relationship("ContestantDocument", back_populates="contestant")
    fees = relationship("RegistrationFee", back_populates="contestant")
    titleholder_record = relationship("Titleholder", uselist=False, back_populates="contestant")
    score_entries = relationship("ScoreEntry", back_populates="contestant")


class ContestantDocument(Base):
    __tablename__ = "contestant_documents"

    id = Column(Integer, primary_key=True, index=True)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # waiver, media_release, bio, resume, etc.
    file_url = Column(String(500), nullable=False)
    signed_date = Column(Date, nullable=True)
    version = Column(Integer, default=1)

    contestant = relationship("Contestant", back_populates="documents")


class RegistrationFee(Base):
    __tablename__ = "registration_fees"

    id = Column(Integer, primary_key=True, index=True)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    fee_type = Column(String(50), nullable=False)  # early, standard, late, door
    amount = Column(Float, nullable=False)
    status = Column(SAEnum(FeeStatus), default=FeeStatus.pending)
    payment_method = Column(String(50), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    receipt_sent = Column(Boolean, default=False)

    contestant = relationship("Contestant", back_populates="fees")


# ── Score Entry ────────────────────────────────────────────────────────

class ScoreEntry(Base):
    __tablename__ = "score_entries"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    judge_id = Column(Integer, ForeignKey("judges.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("competition_categories.id"), nullable=False)
    division_id = Column(Integer, nullable=True)
    score_value = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_synced = Column(Boolean, default=True)  # false for offline entries

    pageant = relationship("Pageant", back_populates="score_entries")
    contestant = relationship("Contestant", back_populates="score_entries")
    judge = relationship("Judge", back_populates="score_entries")
    category = relationship("CompetitionCategory", back_populates="score_entries")


class TabulationRun(Base):
    __tablename__ = "tabulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    division_id = Column(Integer, nullable=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="in_progress")  # in_progress, completed, verified

    pageant = relationship("Pageant", back_populates="tabulation_runs")
    results = relationship("Result", back_populates="tabulation_run")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    tabulation_run_id = Column(Integer, ForeignKey("tabulation_runs.id"), nullable=False)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    division_id = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    total_score = Column(Float, nullable=True)
    is_winner = Column(Boolean, default=False)
    is_runner_up = Column(Boolean, default=False)
    side_awards = Column(JSON, nullable=True)

    tabulation_run = relationship("TabulationRun", back_populates="results")


# ── Sponsor / Donor ────────────────────────────────────────────────────

class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    business_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)

    pageant = relationship("Pageant", back_populates="sponsors")
    agreements = relationship("SponsorshipAgreement", back_populates="sponsor")


class SponsorshipTier(Base):
    __tablename__ = "sponsorship_tiers"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Platinum, Gold, Silver, Bronze
    minimum_amount = Column(Float, nullable=True)
    benefits_description = Column(Text, nullable=True)

    pageant = relationship("Pageant", back_populates="sponsorship_tiers")


class SponsorshipAgreement(Base):
    __tablename__ = "sponsorship_agreements"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("sponsorship_tiers.id"), nullable=True)
    amount = Column(Float, nullable=True)
    in_kind_value = Column(Float, default=0.0)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(SAEnum(AgreementStatus), default=AgreementStatus.active)

    sponsor = relationship("Sponsor", back_populates="agreements")


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    donor_name = Column(String(255), nullable=False)
    donor_type = Column(String(50), default="individual")  # individual, business
    amount = Column(Float, nullable=True)
    in_kind_description = Column(Text, nullable=True)
    receipt_sent = Column(Boolean, default=False)
    thank_you_sent = Column(Boolean, default=False)
    donation_date = Column(DateTime, default=datetime.utcnow)

    pageant = relationship("Pageant", back_populates="donations")


class BarterAgreement(Base):
    __tablename__ = "barter_agreements"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    partner_name = Column(String(255), nullable=False)
    service_provided = Column(Text, nullable=True)
    promotion_provided_in_exchange = Column(Text, nullable=True)
    value_estimate = Column(Float, nullable=True)
    written_agreement_url = Column(String(500), nullable=True)
    status = Column(String(50), default="active")

    pageant = relationship("Pageant", back_populates="barter_agreements")


# ── Marketing ──────────────────────────────────────────────────────────

class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    campaign_type = Column(String(50), nullable=False)  # email, social, print, event
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, nullable=True)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.draft)

    pageant = relationship("Pageant", back_populates="marketing_campaigns")
    email_templates = relationship("EmailTemplate", back_populates="campaign")
    social_posts = relationship("SocialMediaPost", back_populates="campaign")


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("marketing_campaigns.id"), nullable=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True)

    campaign = relationship("MarketingCampaign", back_populates="email_templates")


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("marketing_campaigns.id"), nullable=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # facebook, instagram, tiktok, twitter
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    status = Column(SAEnum(PostStatus), default=PostStatus.draft)

    campaign = relationship("MarketingCampaign", back_populates="social_posts")


# ── Program Book ───────────────────────────────────────────────────────

class ProgramBook(Base):
    __tablename__ = "program_books"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False, unique=True)
    format = Column(String(50), default="printed_and_digital")
    print_run_count = Column(Integer, nullable=True)
    distribution_strategy = Column(String(255), default="every_contestant")
    front_cover_image = Column(String(500), nullable=True)
    director_welcome_text = Column(Text, nullable=True)
    template_id = Column(String(100), nullable=True)

    pageant = relationship("Pageant", back_populates="program_book")


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    program_book_id = Column(Integer, ForeignKey("program_books.id"), nullable=False)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    advertiser_name = Column(String(255), nullable=False)
    advertiser_type = Column(String(50), nullable=False)  # business, contestant_family, sponsor, alumni
    ad_size = Column(String(50), nullable=False)  # business_card, quarter_page, half_page, full_page, back_cover
    file_url = Column(String(500), nullable=True)
    status = Column(String(50), default="submitted")  # submitted, approved, placed
    fee = Column(Float, default=0.0)
    paid = Column(Boolean, default=False)

    pageant = relationship("Pageant", back_populates="ads")


# ── Titleholder ────────────────────────────────────────────────────────

class Titleholder(Base):
    __tablename__ = "titleholders"

    id = Column(Integer, primary_key=True, index=True)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    reign_start_date = Column(Date, nullable=False)
    reign_end_date = Column(Date, nullable=True)
    status = Column(SAEnum(TitleholderStatus), default=TitleholderStatus.active)
    contract_url = Column(String(500), nullable=True)

    contestant = relationship("Contestant", back_populates="titleholder_record")
    contract = relationship("TitleholderContract", uselist=False, back_populates="titleholder")
    appearances = relationship("Appearance", back_populates="titleholder")
    appearance_requests = relationship("AppearanceRequest", back_populates="titleholder")
    points = relationship("TitleholderPoint", back_populates="titleholder")
    removal_proceeding = relationship("TitleRemovalProceeding", uselist=False, back_populates="titleholder")


class TitleholderContract(Base):
    __tablename__ = "titleholder_contracts"

    id = Column(Integer, primary_key=True, index=True)
    titleholder_id = Column(Integer, ForeignKey("titleholders.id"), nullable=False, unique=True)
    signed_date = Column(Date, nullable=True)
    terms = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)

    titleholder = relationship("Titleholder", back_populates="contract")


class Appearance(Base):
    __tablename__ = "appearances"

    id = Column(Integer, primary_key=True, index=True)
    titleholder_id = Column(Integer, ForeignKey("titleholders.id"), nullable=False)
    event_name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(500), nullable=True)
    appearance_type = Column(String(50), nullable=True)  # parade, school, charity, sponsor, media
    notes = Column(Text, nullable=True)
    hours_logged = Column(Float, nullable=True)

    titleholder = relationship("Titleholder", back_populates="appearances")


class AppearanceRequest(Base):
    __tablename__ = "appearance_requests"

    id = Column(Integer, primary_key=True, index=True)
    titleholder_id = Column(Integer, ForeignKey("titleholders.id"), nullable=False)
    requester_name = Column(String(255), nullable=True)
    requester_contact = Column(String(255), nullable=True)
    event_name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SAEnum(AppearanceStatus), default=AppearanceStatus.pending)

    titleholder = relationship("Titleholder", back_populates="appearance_requests")


class TitleholderPoint(Base):
    __tablename__ = "titleholder_points"

    id = Column(Integer, primary_key=True, index=True)
    titleholder_id = Column(Integer, ForeignKey("titleholders.id"), nullable=False)
    point_value = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    point_date = Column(Date, default=date.today)
    category = Column(String(50), nullable=True)  # appearance, community_service, referral, promotion

    titleholder = relationship("Titleholder", back_populates="points")


class TitleRemovalProceeding(Base):
    __tablename__ = "title_removal_proceedings"

    id = Column(Integer, primary_key=True, index=True)
    titleholder_id = Column(Integer, ForeignKey("titleholders.id"), nullable=False, unique=True)
    date_initiated = Column(DateTime, default=datetime.utcnow)
    grounds = Column(String(50), nullable=True)  # contract_violation, reputation_damage, missed_appearances, misconduct
    documentation_notes = Column(Text, nullable=True)
    communication_log = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)
    effective_date = Column(Date, nullable=True)

    titleholder = relationship("Titleholder", back_populates="removal_proceeding")


# ── Financial ──────────────────────────────────────────────────────────

class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"

    id = Column(Integer, primary_key=True, index=True)
    pageant_id = Column(Integer, ForeignKey("pageants.id"), nullable=False)
    category = Column(String(50), nullable=False)  # venue, staffing, awards, marketing, printing, miscellaneous
    description = Column(String(255), nullable=False)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    vendor_name = Column(String(255), nullable=True)
    status = Column(SAEnum(BudgetStatus), default=BudgetStatus.budgeted)

    pageant = relationship("Pageant", back_populates="budget_line_items")
