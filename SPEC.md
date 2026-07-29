# Pageantry Application — Technical Specification

**Based on:** *Directing Pageants: A Master Guide* by Tamsyn J. Simon  
**Reference Site:** www.PageantDirectorResource.com  
**Status:** Greenfield Application Specification  
**Date:** July 29, 2026  

---

## Table of Contents
1. [Overview & Guiding Principles](#1-overview--guiding-principles)
2. [System Architecture & Cross-Cutting Concerns](#2-system-architecture--cross-cutting-concerns)
3. [Domain 1: Pageant Management (Director-Facing)](#3-domain-1-pageant-management-director-facing)
4. [Domain 2: Pageant Day Operations](#4-domain-2-pageant-day-operations)
5. [Domain 3: Post-Pageant](#5-domain-3-post-pageant)
6. [Domain 4: Contestant/Titleholder Portal](#6-domain-4-contestanttitleholder-portal)
7. [Domain 5: Financial System](#7-domain-5-financial-system)
8. [Data Model / Entity Relationship Summary](#8-data-model--entity-relationship-summary)
9. [User Roles & Permissions Matrix](#9-user-roles--permissions-matrix)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Future / Optional Considerations](#11-future--optional-considerations)
12. [Appendices & Book References](#12-appendices--book-references)

---

## 1. Overview & Guiding Principles

### 1.1 Purpose
The Pageantry Application is a greenfield SaaS platform that enables independent pageant directors to plan, manage, execute, and follow up on pageant events. It is built around the domain knowledge, workflows, and best practices codified in *Directing Pageants: A Master Guide*.

### 1.2 Target Users
- **Independent pageant directors** running local, regional, fair, festival, and fundraiser pageants
- **Assistant directors** and co-directors sharing administrative load
- **Judges** who need scoring interfaces
- **Tabulators** who need secure score aggregation tools
- **Contestants** and their families who need registration, schedule, and results access
- **Sponsors** who need visibility into their sponsorship agreements and recognition

### 1.3 Guiding Principles from the Book
1. **Paperwork does the heavy lifting** — written policies, rules, and contracts prevent conflict (Ch. 10, p. 94)
2. **Fairness and transparency are non-negotiable** — judges from outside the area, no sponsor influence, consistent rule enforcement (Ch. 7, p. 74–80)
3. **Systems before reliance** — a healthy pageant runs on systems, not the director's memory (Ch. 17, p. 161)
4. **Simple done well beats elaborate done poorly** — stage décor, scoring, program books, everything (Ch. 6 p. 71, Ch. 7 p. 79)
5. **Community is everything** — relationships with sponsors, contestants, and local entities sustain the pageant (Ch. 9, Ch. 17)
6. **Digital + printed hybrid** — best of both worlds for paperwork, program books, and scoring (Ch. 10, p. 99)

---

## 2. System Architecture & Cross-Cutting Concerns

### 2.1 Multi-Tenancy Model
- **Tenant = Director.** Each director (or director team) is a tenant.
- A single director may run **multiple pageants** under the same account (e.g., a spring festival pageant and a fall scholarship pageant).
- Data is strictly isolated per tenant. Pageants, contestants, judges, sponsors, and financial records of one director are invisible to another.
- **Super-admin** role for platform operators (manage tenants, billing, support).

### 2.2 Architectural Pattern
- **Web-first (responsive SPA)** with progressive offline capability for pageant day.
- **API-first** design — all functionality accessible via REST/GraphQL API.
- **Offline-first for Pageant Day** — check-in, scoring, tabulation, and backstage tools must work with intermittent connectivity and sync when reconnected.
- Optional **native mobile wrappers** for judges (scoring app) and backstage (lineup view).

### 2.3 User Roles & Permissions
See [Section 9: User Roles & Permissions Matrix](#9-user-roles--permissions-matrix) for full details.

### 2.4 Notifications & Communication
- **Email** — triggered by registration, deadline reminders, results, sponsor thank-yous
- **SMS / text** — day-of reminders, contestant lineup changes, urgent announcements
- **In-app notifications** — for director, tabulator, and judge workflows
- **Template engine** — the book stresses clear, consistent communication (Ch. 10, p. 97); the app should provide editable templates for all common messages
- **24-hour policy** — post-pageant communication lockout window supported by auto-responder configuration (Ch. 14, p. 129)

### 2.5 Document Management
- Cloud-based file storage per pageant
- Support for: PDF, DOCX, PNG, JPG, spreadsheets
- **Version control** — the book emphasizes version tracking for rulebooks and forms (Ch. 10, p. 101)
- **Template library** — pre-built templates for registration forms, judge handbooks, emcee scripts, titleholder contracts, and program books, all reflecting PDR Store templates (the book references templates at PageantDirectorResource.com)
- **Auto-retire outdated versions** — directors mark a version active; previous versions archived but accessible

### 2.6 Multi-Language / Locale
- English first (the book is in English with US-centric community references)
- Locale-aware date formatting, currency, and pageant-community conventions

---

## 3. Domain 1: Pageant Management (Director-Facing)

### 3.1 Pageant Creation & Configuration

**Purpose / User Story:** *As a director, I want to create a new pageant in the system, configure its identity, rules, structure, and branding, so that everything downstream (registration, judging, scheduling) inherits these settings.*

**Book Reference:** Ch. 2 (Strong Beginnings), Ch. 4 (Structuring Your Pageant)

**Key Entities:**
- `Pageant` — id, tenant_id, name, mission_statement, slug, status (draft/active/archived)
- `PageantBranding` — logo_url, color_palette, slogan, font_preferences
- `PageantSetting` — key-value settings for the pageant (e.g., `judges_count`, `allow_door_entries`, `default_currency`)

**Functional Requirements:**
- Create pageant with name, mission statement (the book's 5-step process, Ch. 2, p. 11)
- Configure pageant type: **Representative** (winners serve as ambassadors, active year-long reign) or **Hobby** (one-day, no ongoing duties) (Book p. 12, p. 132)
- Branding: upload logo, set color palette (gold/deep blue = prestige, pink/pastels = fun, black/silver = modern — per Ch. 3, p. 51), set slogan
- Upload and manage multiple versions of logo; the book warns against separate logos for every use (p. 52)
- Business structure selection: Sole Proprietor / LLC / Corporation / Nonprofit — stored as metadata (Ch. 2, p. 15)
- Integration for **Pageant Box** (physical file box concept) — the app replaces the physical box with a digital command center (Ch. 2, p. 19)
- Email/digital file structure per book's suggested hierarchy (Ch. 2, p. 20)

### 3.2 Age Divisions & Competition Categories

**Purpose:** *As a director, I want to define age divisions and competition categories so that contestants know what they are competing in and judges know how to score.*

**Book Reference:** Ch. 4, p. 29–34

**Key Entities:**
- `AgeDivision` — id, pageant_id, name (e.g., "Tiny Miss"), min_age, max_age, gender, age_as_of_date, eligibility_rules, residency_requirements, marital_status_rules
- `CompetitionCategory` — id, division_id, name (e.g., "Formalwear"), type (on_stage / off_stage / optional), order, scoring_weight, time_limit_seconds
- `SideEvent` — id, pageant_id, name (e.g., "Photogenic", "Crowd Favorite"), type, fee, is_optional, is_fundraiser

**Functional Requirements:**
- Define age divisions with age ranges (e.g., 0–18 months Baby Miss, 19–35 months Wee Miss, 3–4 Tiny Miss, 5–7 Little Miss, etc. — Book p. 30)
- Flexible grouping: combine ages within a division, split by single years as pageant grows
- Court vs. Junior Court concept (e.g., active titleholders vs. fun-only competition) — Book p. 30
- Competition categories library: Formalwear, Casualwear, Outfit of Choice, Fun Fashion, Themewear, Swimwear, Activewear, Photogenic, Portfolio, Interview, On Stage Question, Personal Introduction, Talent, Community Service, Academic Achievement, Spokesmodel, Resume, Thank You Note, Scrapbook, Donations, Ad Sales, Crowd Favorite, People's Choice, Referral Queen, Door Titles (Book p. 31–35)
- For each category: define scoring rules, time limits, attire guidelines, music preferences
- Optional categories with separate fees (à la carte pricing model) — Book p. 37
- Production number configuration (opening number, participants, song, length, attire) — Book p. 40
- Stage formation configuration: Diamond, V, Back T, Front T, Figure 8, Circle — Book p. 44–45, including configurable X markers

### 3.3 Scoring System Configuration

**Purpose:** *As a director, I want to configure scoring rubrics, judge panels, and tabulation rules so that the competition is fair, transparent, and efficient.*

**Book Reference:** Ch. 7 (Judges, Tabulators, & Scoring)

**Key Entities:**
- `ScoringRubric` — id, pageant_id, category_id, name, max_score (e.g., 10), allow_half_points (true/false), scoring_criteria_text
- `ScoringScale` — description of what each score level means (e.g., 1–3 = Needs Improvement, 4–6 = Average, 7–8 = Above Average, 9–10 = Excellent)
- `JudgePanel` — id, pageant_id, judges (many-to-many with Judge), head_judge_id, orientation_date, backup_judge_id
- `TieBreakRule` — id, pageant_id, method (head_judge_decides / re-score / highest_specific_category / etc.)
- `ScoreDistributionPolicy` — day-of (contestants get scoresheets immediately), post-pageant (mailed/emailed), pay-for-scores, or no scoresheets (Book p. 80)

**Functional Requirements:**
- Configure custom scoring rubrics per category
- Whole and half-number scoring (e.g., 8.5, 9) — Book p. 79
- Scoresheets with: scoring scale, comment section for constructive feedback, judge initial area, pre-printed contestant info or blank spaces
- Configurable judges panel (3–4 judges standard, more for larger productions) — Book p. 74
- Head Judge designation with tie-breaking authority — Book p. 80
- Multi-round elimination or cumulative scoring
- Comment section on every scoresheet (the book says contestants "deserve to understand why they received their scores" — p. 79)
- Print or digital scoresheet delivery to contestants
- **Tabulator** role with dedicated tools (see Domain 2)

### 3.4 Contestant Registration & Management

**Purpose:** *As a director, I want contestants to register, submit paperwork, and manage their profiles so that I have all required information before pageant day.*

**Book Reference:** Ch. 10 (Paperwork Development & Distribution), Ch. 4 (Contestant Bios)

**Key Entities:**
- `Contestant` — id, pageant_id, division_id, first_name, last_name, age, birthdate, address, phone, email, emergency_contact, photo_url, status (registered/checked_in/competed/no_show)
- `ContestantDocument` — id, contestant_id, type (registration_form / waiver / media_release / bio / resume / platform_statement / photo_contest_entry), file_url, signed_date, version
- `RegistrationFee` — id, contestant_id, fee_type (early / standard / late / door), amount, status (pending/paid/refunded), payment_method, payment_date

**Functional Requirements:**
- Online registration with all fields per book's Information & Registration Form (p. 95–96)
- Age verification — "Age as of ___" date enforcement
- Eligibility checks: residency restrictions, marital/parental status, age division mapping
- Document upload: headshot, bio, resume, platform statement, media release, liability waiver
- Standardized bio format per Book p. 39 — headshot + resume-style summary for Miss divisions, fun/activity-centered bios for younger divisions
- Platform statement collection for contestants with required platforms (p. 39)
- Fee management: tiered pricing (early/standard/late/door), discounts, referral credits, refund tracking
- Deadline management with configurable cutoffs
- Waitlist handling if divisions fill
- Contestant number assignment
- Registration form should include: code of conduct, liability waiver, photo/media release, refund policy acknowledgement — per p. 96
- The book suggests an **FAQ** module on the website to reduce repetitive questions (p. 98)

### 3.5 Scheduling

**Purpose:** *As a director, I want to manage pageant dates, rehearsal scheduling, and conflict-checking against other pageants so that I maximize contestant turnout.*

**Book Reference:** Ch. 5 (When to Crown)

**Key Entities:**
- `PageantSchedule` — id, pageant_id, pageant_date, doors_open_time, start_time, estimated_end_time, day_of_week, timezone
- `Rehearsal` — id, pageant_id, date, start_time, end_time, location, mandatory (boolean), notes
- `ConflictCheck` — id, pageant_id, radius_miles (default 120 for 2-hour radius), conflicting_pageants (JSON array of detected conflicts)
- `CommunityEvent` — id, name, date, location, type (fair / festival / school_event / sports / holiday), notes

**Functional Requirements:**
- Date selection with integrated calendar view
- Conflict checking: auto-detect known pageants within 2-hour radius (Book p. 62)
- School calendar integration (avoid start/end of school year, homecomings, proms, testing periods, graduations — p. 61)
- Community event integration: check community calendars for fairs, festivals, car shows, major sporting events
- Multi-day scheduling support (e.g., Friday younger divisions, Saturday main event — p. 60)
- Time selection guidance: avoid nap times for babies (mid-morning/early evening), evening for Teen/Miss divisions, traffic pattern consideration, lighting conditions — p. 60
- Rehearsal scheduling with RSVP tracking
- Split division scheduling (younger on Friday, older on Saturday)
- The book recommends checking pageant-specific social media calendars and Facebook "events like this" feature (p. 62) — the app could aggregate this

### 3.6 Venue Management

**Purpose:** *As a director, I want to manage venue details, contracts, capacity, costs, and stage layout so that I can plan effectively and avoid surprises.*

**Book Reference:** Ch. 6 (Selecting a Venue)

**Key Entities:**
- `Venue` — id, name, address, contact_name, contact_phone, contact_email, capacity, stage_dimensions, has_built_in_stage, parking_info, accessibility_notes
- `VenueContract` — id, venue_id, pageant_id, contract_start_date, contract_end_date, rental_cost, deposit_amount, deposit_due_date, balance_due_date, insurance_requirements, cancellation_terms, file_url, status (draft/signed/expired)
- `VenueAmenity` — id, venue_id, amenity_type (chairs / tables / sound_system / lighting / dressing_rooms / green_room / kitchen / parking / wifi), included_in_rental (boolean), cost_if_not_included
- `VenueLayout` — id, venue_id, pageant_id, stage_formation (diamond/v/back_t/front_t/figure_8/circle), registration_table_location, dressing_area_location, judges_table_location, seating_capacity_used

**Functional Requirements:**
- Venue database with search/filter (by capacity, location, amenities, cost range)
- Contract management: upload, track key dates, deposit tracking, payment milestones
- Venue cost calculators: (venue_cost / capacity = ticket_price_feasibility) — Book p. 69
- Cost-saving strategy tracking: timing discounts (Friday/Sunday), shared venue opportunities, event partnerships, hotel discounts, vendor space — p. 69
- Venue walk-through checklist: red flags (unclear contracts, hidden fees, limited access, no dressing area, poor lighting/sound — p. 65)
- Stage layout designer: drag-and-drop with X markers for stage formations (Diamond, V, T formations per p. 44–45)
- Dressing area configuration: lighting, electrical access, tables, chairs, privacy — p. 67
- Green room configuration: finger foods, drinks, seating, lighting — p. 67
- Seating estimation: Anticipated Contestants × 3 = audience estimate — p. 67
- Accessibility checklist: parking (free / on-site / accessible — aim for 2 of 3 — p. 66)
- Stage decoration planner: balloon garlands, backdrop systems, pageant branding (logo banner), greenery — p. 70–71
- Venue restriction tracker (no nails, tape, confetti, open flames — p. 71)

### 3.7 Sponsor & Donor Management

**Purpose:** *As a director, I want to manage sponsors, donation tiers, in-kind contributions, and barter agreements so that I can fund my pageant transparently.*

**Book Reference:** Ch. 9 (Funding Your Pageant: Sponsorships, Donations & Smart Bartering)

**Key Entities:**
- `Sponsor` — id, pageant_id, business_name, contact_name, contact_email, contact_phone, address, website, logo_url
- `SponsorshipTier` — id, pageant_id, name (Platinum / Gold / Silver / Bronze / Presenting / Division / Crown / Sash / Scholarship), minimum_amount, benefits_description (social_media_features / program_ad / signage / on_stage_mention / booth_space)
- `SponsorshipAgreement` — id, sponsor_id, tier_id, amount, in_kind_value, start_date, end_date, status (active/fulfilled/expired)
- `Donation` — id, pageant_id, donor_name, donor_type (individual / business), amount, in_kind_description, receipt_sent (boolean), thank_you_sent (boolean), date
- `BarterAgreement` — id, pageant_id, partner_name, service_provided, promotion_provided_in_exchange, value_estimate, written_agreement_url, status

**Functional Requirements:**
- Sponsor directory with contact management
- Sponsorship packet generator (tier descriptions, benefits, recognition details — p. 89)
- Targeted business suggestions: salons, boutiques, photographers, fitness studios, community organizations (p. 89)
- In-kind donation tracking: product donations, gift certificates, services, venue, equipment (p. 90)
- Conflict of interest flagging — sponsors/donors must NOT have a contestant competing (p. 91)
- Sponsor recognition automation: social media posts, program book ad placement, on-stage mention scheduling
- Thank-you note generator (handwritten-style templates)
- Barter agreement tracking with value estimation and written agreement storage (p. 92)
- Barter restrictions: no bartering for judges, no contestant family conflicts (p. 92)

### 3.8 Marketing Tools

**Purpose:** *As a director, I want to plan and execute marketing campaigns — email, social media, print — so that I attract contestants, sponsors, and audience.*

**Book Reference:** Ch. 11 (Marketing 101)

**Key Entities:**
- `MarketingCampaign` — id, pageant_id, name, type (email / social / print / event), start_date, end_date, budget, status
- `EmailTemplate` — id, pageant_id, name, subject, body, variables (e.g., {{contestant_name}}, {{pageant_date}})
- `SocialMediaPost` — id, pageant_id, platform (facebook / instagram / tiktok / twitter), content, media_urls, scheduled_date, status (draft/scheduled/published)
- `ContestantReferral` — id, referring_contestant_id, referred_contestant_id, code, discount_amount, date

**Functional Requirements:**
- Email campaign builder with templates for: registration announcement, deadline reminders, countdowns, sponsor shoutouts
- Automated sequences: welcome series for new inquiries, periodic reminders (p. 107)
- Social media post scheduler with platform-specific guidance (Facebook for event details, Instagram for visual content, TikTok/Reels for short-form video — p. 106)
- Hashtag manager: create unique pageant hashtag, encourage contestant use (p. 106)
- Countdown post automation (daily updates in final week — p. 108)
- Titleholder takeover coordination (schedule titleholder-led social media days — p. 108)
- Referral program tracking: referral line on registration forms, referral queen award (p. 35, p. 107)
- Flyer/poster design tool with templates (QR code to website, key details — p. 106)
- Printed material distribution log (track where flyers are posted)
- Live Q&A session scheduler

### 3.9 Program Book Management

**Purpose:** *As a director, I want to manage program book ad sales, layout, and distribution so that program books generate revenue and enhance professionalism.*

**Book Reference:** Ch. 12 (More Than A Souvenir: The Power of a Program Book)

**Key Entities:**
- `ProgramBook` — id, pageant_id, format (printed / digital / both), print_run_count, distribution_strategy (every_contestant / sell_at_door / sponsor_complimentary / digital_download)
- `Ad` — id, program_book_id, advertiser_name, advertiser_type (business / contestant_family / sponsor / alumni), ad_size (business_card / quarter_page / half_page / full_page / back_cover), file_url (print_ready), status (submitted / approved / placed), fee, paid (boolean)
- `ProgramBookLayout` — id, program_book_id, front_cover_image, director_welcome_text, contestant_section_order, ad_section_order, template_id

**Functional Requirements:**
- Ad sales management: multiple sizes, pricing, submission tracking
- Print-ready ad requirements: 300 DPI, PDF/PNG/JPG, correct dimensions (p. 113)
- Template-based layout: front cover (pageant name, date, logo), inside cover (welcome letter), contestant section (name, photo, bio per division), ad section (organized by size/tier), back cover (thank-you or photo contest — p. 112)
- Digital program book generation (PDF + web view)
- Print-on-demand integration or print shop file export
- Contestant ad sales tracking — who sold the most ads (award tracking)
- Sponsor ad placement by tier
- Back cover photo contest support (revenue opportunity mentioned on p. 112)
- Distribution tracking: every contestant gets one, sell at door, complimentary for sponsors/judges, digital access
- The book recommends printing 10% more than contestant count (p. 114)
- Simple alternatives: single-page handout, black-and-white booklet, digital-only (p. 112)

### 3.10 Titleholder Management

**Purpose:** *As a director, I want to manage titleholder reigns — track appearances, community service, communication, and title removal procedures — so that my brand is protected and titleholders succeed.*

**Book Reference:** Ch. 15 (Managing Your Titleholders), Ch. 16 (Handling the Negative)

**Key Entities:**
- `Titleholder` — id, contestant_id, title_id, division_id, reign_start_date, reign_end_date, status (active / completed / removed / resigned), contract_url
- `TitleholderContract` — id, titleholder_id, signed_date, terms (appearance_requirements, conduct_standards, communication_guidelines, crown_sash_return_terms)
- `Appearance` — id, titleholder_id, event_name, date, location, type (parade / school_visit / charity / sponsor_event / media), notes, hours_logged
- `AppearanceRequest` — id, titleholder_id, requester_name, requester_contact, event_name, date, status (pending / approved / declined / completed)
- `TitleholderPoint` — id, titleholder_id, point_value, reason, date, category (appearance / community_service / referral / promotion)
- `TitleRemovalProceeding` — id, titleholder_id, date_initiated, grounds (contract_violation / reputation_damage / missed_appearances / misconduct), documentation_notes, communication_log, outcome, effective_date

**Functional Requirements:**
- Titleholder profile: contact info, reign timeline, photo gallery, contracts
- Contract management: titleholder agreement templates per Book's guidance (p. 133)
- Appearance calendar and request workflow
- Appearance log with hours tracking (community service documentation)
- Point-based system for "Queen of the Year" or "Queen of Queens" awards — referral points, appearance points, promotional participation (p. 135)
- Communication log: track all director-titleholder interactions
- Conduct tracking with warning system
- **Title removal workflow** — structured process with:
  - Grounds documentation (contract violation, reputation damage, missed appearances, misconduct — p. 144)
  - Pre-removal checklist (6 questions from p. 145)
  - Communication templates for removal notification (p. 145–146)
  - Crown/sash return tracking
  - Post-removal review for system improvement
- "One and Done" titleholder management: post-pageant message, crowning invitation for next year, no assumed participation (p. 135)
- Outgoing queen recognition: acknowledgment, thank-you note, social media post, keepsake (p. 125)
- Sister-queen relationship builder: group messaging, shared calendar

---

## 4. Domain 2: Pageant Day Operations

### 4.1 Pre-Arrival / Director Prep

**Book Reference:** Ch. 13 (Pageant Day), p. 117–118

**Functional Requirements:**
- Director's day-of dashboard: consolidated view of all pre-arrival checklists
- **"Just in Case" Kit digital list**: office supplies, safety pins, tape, scissors, snacks, water (p. 118)
- Schedule confirmation: final timeline visible to all staff
- Arrival order planner: director first, then key staff, then contestants
- Venue walk-through checklist with photo attachment

### 4.2 Contestant Check-In

**Book Reference:** Ch. 13, p. 119

**Functional Requirements:**
- Digital check-in workflow: scan or search contestant, confirm registration, mark arrival
- Paperwork collection verification (waivers, media releases, remaining fees)
- Contestant number distribution tracking
- Dressing area assignment
- Admission ticket verification for families
- **Orientation** module (optional) — for scholarship-style multi-event pageants needing a brief overview (p. 119)
- Real-time contestant arrival dashboard for director

### 4.3 Judge Interface

**Book Reference:** Ch. 7, p. 75–80; Ch. 13, p. 120

**Functional Requirements:**
- **Digital scoresheet application** (laptop/tablet-based or paper fallback):
  - Per-contestant scoring with scoring scale reference
  - Comment section for constructive feedback on every score (p. 79)
  - Judge initial field
  - Pre-populated contestant names/numbers or blank entry
- **Judge's Handbook** digital delivery — sent 1 week before, accessible on device (p. 76)
- Offline mode: scores cached locally, sync when reconnected
- Backend tabulator view: real-time (but hidden from judges) score collection
- Head Judge dashboard: tie-breaking tools, discussion mode
- Backup judge onboarding (p. 75)

### 4.4 Backstage Management

**Book Reference:** Ch. 13, p. 121–122

**Functional Requirements:**
- **Lineup management**: digital contestant order by category/division
- Real-time lineup display (backstage monitor or tablet)
- Status tracking: waiting / on deck / on stage / completed
- No-show alerting: notify emcee and judges quietly
- Wardrobe malfunction / delay communication channel
- Backstage helper view: see who needs to be collected from dressing room
- Backstage access control: only authorized personnel (p. 121)
- Parent/coach boundary enforcement — clearly defined who is allowed backstage
- Music cue integration: per-contestant music, "press play and forget it" mode for simpler events (p. 122)

### 4.5 Real-Time Scoring & Tabulation

**Book Reference:** Ch. 7, p. 77–80

**Key Entities:**
- `ScoreEntry` — id, scoresheet_id, contestant_id, judge_id, category_id, score_value, comment, timestamp
- `TabulationRun` — id, pageant_id, division_id, run_timestamp, status (in_progress / completed / verified)
- `Result` — id, tabulation_run_id, contestant_id, division_id, rank, is_winner, is_runner_up, side_awards (JSON)

**Functional Requirements:**
- Tabulator dashboard: collect scores from all judges for current category/division
- Automatic score aggregation (sum, average, weighted)
- Real-time rank calculation
- Tie detection and resolution workflow (p. 80):
  - Head Judge makes final decision after brief discussion
  - Or pre-configured tie-breaking by highest score in specific category
- Verification checkpoint: tabulator marks run as verified before results are final
- Paper backup workflow: tabulator can enter paper scores manually
- **Double-entry verification**: two calculators, two sets of master lists (the book provides two calculators for redundancy — p. 77)
- **Red pen** for tabulator to distinguish from judge ink (p. 77)
- Scoresheet distribution:
  - Day-of: print or digital delivery by contestant number
  - Post-pageant: email or mail (with SASE tracking)
- The book strongly encourages giving contestants their scoresheets (p. 80)
- Comment moderation — ensure judge comments are constructive and positive

### 4.6 Crowd Favorite / Fundraising Vote Tracking

**Book Reference:** Ch. 4, p. 35, 38

**Functional Requirements:**
- Real-time vote counter for Crowd Favorite ($1 per vote — p. 35, 38)
- Online voting portal before the event (People's Choice — p. 35)
- Live vote count display for audience engagement
- Cash + digital payment integration for votes
- Overall Crowd Favorite with "showstopping, oversized crown" option (p. 35)
- Referral tracking line on registration (p. 35)

### 4.7 Production Number Coordination

**Book Reference:** Ch. 4, p. 40

**Functional Requirements:**
- Production number planner: song selection, length (2 min for small groups), participant list
- Attire assignment (e.g., "short blue dress" color/style — p. 40)
- Rehearsal scheduling integration
- Outgoing royalty opening number choreography
- The book suggests pageant t-shirt + white shorts for a clean, uniformed look

### 4.8 Award Ceremony Flow

**Book Reference:** Ch. 4, p. 41–43; Ch. 13, p. 124–126

**Functional Requirements:**
- Award staging: crown, sash, flowers, certificates pre-staged per division
- Award order configurator (queen first, runners-up, side awards; or reverse)
- Emcee script integration — award sequence displayed to emcee
- Photo flow after crowning: on-stage vs. side-stage, communicated in advance (p. 126)
- Outgoing queen farewell: recognition moment, thank-you, keepsake (p. 125)
- The book advises slowing the pace for crowning — "allow pauses for announcements, applause, and emotion" (p. 124)

---

## 5. Domain 3: Post-Pageant

### 5.1 Results Publishing

**Book Reference:** Ch. 14 (After the Curtains Close)

**Functional Requirements:**
- Results dashboard: final standings per division
- Public results page (opt-in) for website/social media
- Score distribution to contestants (day-of or post-pageant)
- Historical results archive across pageant years

### 5.2 Sponsor & Donor Thank-You Automation

**Book Reference:** Ch. 14, p. 128, 130; Ch. 9, p. 90–91

**Functional Requirements:**
- Automated thank-you email/message generation per sponsor tier
- Handwritten note printing support (mailing addresses, envelope stuffing)
- Social media thank-you post scheduler with sponsor tag
- Impact report generator: show sponsors how their support was used (photos, award examples — p. 130)
- Certificate of appreciation generator
- Sponsorship renewal tracking: remind directors to reach out to previous sponsors before next event

### 5.3 Titleholder Onboarding & Management

**Book Reference:** Ch. 15, p. 132–136

**Functional Requirements:**
- Post-crowning onboarding workflow:
  - Titleholder contract digital signature
  - Reign expectations document (active vs. one-and-done — p. 133)
  - Appearance request form access
  - Crown/sash care instructions
- Communication cadence setup: regular check-ins, notification preferences (p. 133)
- Social media style guide for titleholders (brand voice, posting guidelines)
- Titleholder portal access (see Domain 4)

### 5.4 Post-Event Reporting & Analytics

**Book Reference:** Ch. 14, p. 128, 130; Ch. 17, p. 153

**Functional Requirements:**
- Financial summary: revenue (entry fees, admission, program books, votes, sponsorships) vs. expenses (venue, awards, staffing, printing)
- Contestant demographics: age distribution, geographic reach (zip code mapping)
- Marketing analytics: email open rates, social media engagement, referral sources
- Year-over-year comparison: contestant counts, revenue, expenses
- Staff debrief notes: what worked, what to improve (p. 128)
- Director reflection prompts (p. 153): timeline, paperwork, staffing, venue, communication, contestant feedback
- Exportable reports for board, sponsors, or personal records

---

## 6. Domain 4: Contestant/Titleholder Portal

### 6.1 Registration & Paperwork Submission

**Book Reference:** Ch. 10, p. 95–96

**Functional Requirements:**
- Online registration form with all fields from the Information & Registration Form
- Document upload: headshot, bio, resume, platform statement, media release, liability waiver
- Fee payment: credit/debit, PayPal, Square, Venmo, CashApp — the book recommends multiple payment options and QR codes (p. 18)
- Registration status tracking: pending, confirmed, waitlisted
- Auto-generated confirmation email with next steps

### 6.2 Portfolio Upload

**Book Reference:** Ch. 4, p. 33

**Functional Requirements:**
- Photo upload (headshots, full-length, themed) — max 20 photos for efficiency (p. 33)
- Photogenic competition entry management
- Platform statement submission for Miss divisions (typed essay, 12pt font, one page max — p. 39)

### 6.3 Schedule Viewing

**Functional Requirements:**
- Personal schedule showing: check-in time, rehearsal time, competition times by category
- Real-time updates: lineup changes, delays
- Venue info, directions, parking details
- Map of venue layout (registration, dressing room, stage area, seating)

### 6.4 Results & Feedback Access

**Book Reference:** Ch. 7, p. 79–80

**Functional Requirements:**
- Secure results view (after director publishes)
- Digital scoresheet download with judge comments
- Historical comparison across years (if contestant competed before)

### 6.5 Titleholder Appearance Scheduling

**Book Reference:** Ch. 15, p. 134

**Functional Requirements:**
- Appearance request form: event name, date, location, type (parade, school, charity, sponsor, media)
- Request approval workflow (director reviews and approves/declines)
- Calendar sync (Google Calendar, iCal)
- Appearance log: track hours, upload photos, add notes
- Approved messaging and social media guidelines reference

---

## 7. Domain 5: Financial System

### 7.1 Budgeting

**Book Reference:** Ch. 8 (The Cost of Crowning), Ch. 8 p. 83–85

**Key Entities:**
- `BudgetLineItem` — id, pageant_id, category (venue / staffing / awards / marketing / printing / miscellaneous), description, estimated_cost, actual_cost, vendor_name, status (budgeted / ordered / paid)
- `BudgetVersion` — id, pageant_id, version_number, total_estimated, total_actual, created_at

**Functional Requirements:**
- Budget template based on book's cost categories:
  - **Venue** (largest expense, factor hourly vs flat rate, deposit, insurance — p. 83)
  - **Staffing** (tabulator is always paid; judges compensated; volunteers for runners, backstage, setup — p. 84)
  - **Awards** (crowns, sashes, trophies, medallions, certificates — rule of thumb: entry fee of 2 contestants covers division prizes — p. 85)
  - **Marketing & Printing** (program books, flyers, ads)
  - **Miscellaneous** (thank-you notes, judges' candy dish, extra copies — p. 82)
- Actual vs. budget tracking
- Revenue tracking: entry fees (by tier), admission, program book ads, Crowd Favorite, sponsorships, donations
- Fundraiser pageant mode: special strategies (free venue, local judges, reduced tabulator pay, cost-effective prizes, $5-10 admission — p. 86)

### 7.2 Payment Processing

**Book Reference:** Ch. 2, p. 18

**Functional Requirements:**
- Multiple payment methods: credit/debit cards, PayPal, Square, Venmo, CashApp, Zelle, checks/money orders, cash
- Dedicated business account integration (not personal)
- QR code generation for quick payments
- Check/money order tracking: allow time to clear, returned check fee enforcement, no checks on pageant day (p. 18)
- Receipt generation for every transaction
- Refund processing with policy enforcement

### 7.3 Award Cost Planning

**Book Reference:** Ch. 4, p. 41–43; Ch. 8, p. 85

**Functional Requirements:**
- Award budget calculator: tops-down planning (queen prizes first, then runners-up, then side awards)
- Crown comparison tool (vendor, size, style, price per division)
- Sash costing (embroidered satin vs. custom ribbon vs. stock Queen sashes — p. 41)
- Participation award budget (certificates, participation medals, goody bags)
- Silver platter / creative budget-friendly award ideas tracker (p. 43)
- Split award tracking (Themewear scores separated for side title, extra entry fee, larger crown — p. 43)

---

## 8. Data Model / Entity Relationship Summary

### Core Entities & Relationships

```
Tenant (Director)
  ├── Pageant (1..N)
  │   ├── PageantBranding (1:1)
  │   ├── PageantSetting (1:N)
  │   ├── AgeDivision (1:N)
  │   │   └── CompetitionCategory (1:N)
  │   │       └── ScoringRubric (1:1)
  │   ├── SideEvent (1:N)
  │   ├── JudgePanel (1:N)
  │   │   └── Judge (N:M) — through JudgePanelJudge
  │   ├── ScoringScale (1:N)
  │   ├── TieBreakRule (1:N)
  │   ├── VenueContract (N:1 with Venue)
  │   ├── VenueLayout (1:N)
  │   ├── PageantSchedule (1:1 for date; N for rehearsals)
  │   ├── Contestant (1:N)
  │   │   ├── ContestantDocument (1:N)
  │   │   ├── RegistrationFee (1:N)
  │   │   └── Titleholder (0:1)
  │   │       ├── TitleholderContract (1:1)
  │   │       ├── Appearance (1:N)
  │   │       ├── AppearanceRequest (1:N)
  │   │       ├── TitleholderPoint (1:N)
  │   │       └── TitleRemovalProceeding (0:1)
  │   ├── Sponsor (1:N)
  │   │   └── SponsorshipAgreement (1:N with SponsorshipTier)
  │   ├── Donation (1:N)
  │   ├── BarterAgreement (1:N)
  │   ├── ProgramBook (1:1)
  │   │   └── Ad (1:N)
  │   ├── MarketingCampaign (1:N)
  │   │   ├── EmailTemplate (1:N)
  │   │   └── SocialMediaPost (1:N)
  │   ├── ScoreEntry (1:N)
  │   ├── TabulationRun (1:N)
  │   └── BudgetLineItem (1:N)
```

---

## 9. User Roles & Permissions Matrix

| Capability | Director | Asst. Director | Tabulator | Judge | Contestant | Sponsor | Super Admin |
|---|---|---|---|---|---|---|---|
| Create/manage pageant config | ✓ | – | – | – | – | – | ✓ |
| Configure age divisions & categories | ✓ | – | – | – | – | – | ✓ |
| Manage registration forms | ✓ | ✓ (read) | – | – | – | – | ✓ |
| View contestant list | ✓ | ✓ | ✓ (names/numbers only) | ✓ (names/numbers only) | Own data | – | ✓ |
| Configure scoring rubrics | ✓ | – | – | – | – | – | ✓ |
| Enter scores | – | – | – | ✓ | – | – | – |
| View live scores (aggregate) | ✓ | ✓ | ✓ | – | – | – | ✓ |
| Run tabulation | – | – | ✓ | – | – | – | – |
| Verify results | ✓ | ✓ | ✓ (mark verified) | – | – | – | ✓ |
| Manage sponsors/donors | ✓ | ✓ | – | – | – | Own info | ✓ |
| Manage venue contracts | ✓ | ✓ | – | – | – | – | ✓ |
| Submit paperwork | – | – | – | – | ✓ | – | – |
| View own scores | – | – | – | – | ✓ | – | – |
| Submit appearance requests | – | – | – | – | ✓ (titleholders) | – | – |
| Manage titleholder contracts | ✓ | ✓ | – | – | Sign own | – | ✓ |
| View program book | ✓ | ✓ | – | – | ✓ | Own ad | ✓ |
| Access financial reports | ✓ | ✓ | – | – | – | – | ✓ |
| System/billing admin | – | – | – | – | – | – | ✓ |

---

## 10. Non-Functional Requirements

### 10.1 Performance & Scalability
- **Contestant concurrency**: support for 200+ contestants checking in simultaneously at peak pageant day
- **Real-time scoring**: score submission-to-tabulation display in under 2 seconds for panels of up to 10 judges
- **Multi-pageant support**: a single director should manage up to 10 pageants without performance degradation
- **P95 response time**: under 300ms for all API requests except file uploads

### 10.2 Offline Capability
- **Pageant day essential functions must work offline**:
  - Contestant check-in (cache contestant roster locally)
  - Judge score entry (store scores locally, sync when online)
  - Tabulator aggregation (compute ranks client-side)
  - Backstage lineup view
- **Sync conflict resolution**: last-write-wins with audit log for score entries; explicit conflict prompt for registration changes
- Service Worker for web app; SQLite local DB for mobile apps

### 10.3 Reliability & Availability
- **Pageant day target**: 99.9% uptime for scoring and check-in services (the pageant must not stop for server issues)
- **Graceful degradation**: if cloud services unavailable, fallback to paper backup workflow — the app should support a "offline mode" with printed score sheets and manual data entry later
- The book explicitly warns "Technology will eventually fail. Printed backups keep the pageant moving." (Ch. 10, p. 99)

### 10.4 Security
- **Data isolation**: strict tenant-level access control
- **Scores and results**: encrypted at rest and in transit; only tabulator and director see live scores
- **PII protection**: contestant information (address, phone, birthdate, photos) encrypted; access limited to director and authorized staff
- The book says "Directors have an ethical responsibility to protect that information" (Ch. 10, p. 102)
- **Payment data**: PCI-compliant via Stripe/Square integration; no raw card numbers stored

### 10.5 Multi-Tenancy
- **Isolated data per director tenant**
- Optional multi-pageant aggregation for directors running multiple events
- Shared pageant conflict calendar across tenants (opt-in: directors can see when OTHER directors in their area have scheduled — the book discusses the 2-hour radius rule, p. 62)

### 10.6 Accessibility
- WCAG 2.1 AA compliance for contestant portal
- High-contrast mode for on-stage judges' devices
- Screen reader support for registration forms

### 10.7 Data Retention & Export
- Contestant data retained per director's privacy policy (default 3 years post-pageant)
- Full data export (ZIP with JSON + files) on request
- Pageant history preserved even when archived (for legacy and tradition continuity — Ch. 17, p. 161)

---

## 11. Future / Optional Considerations

### 11.1 Mobile Apps
- **Judge App**: offline-first scoring on tablet, sync on reconnection; built-in camera for scoring area photos
- **Backstage App**: lineup view, contestant status, no-show reporting, music cue triggers
- **Titleholder App**: appearance logging, schedule, communication hub, point tracking

### 11.2 Vendor Marketplace
- The book emphasizes building long-term vendor relationships (Ch. 17, p. 150)
- Directory of recommended vendors (crown companies, photographers, florists, print shops)
- Rating/review system for pageant directors
- "Go-to" vendor list per director

### 11.3 Industry-Wide Pageant Calendar
- Shared calendar across the platform where directors can self-report pageant dates
- Auto-conflict detection when a director sets a date within 2 hours/120 miles of another pageant (Book p. 62)
- This is a sensitive feature — must be opt-in and should not expose details of other directors' pageants beyond date and city

### 11.4 AI-Powered Assistance
- **Slogan generator** based on pageant mission (Book's 5-step process, p. 53)
- **Logo design suggestions** based on color palette and brand aesthetic (p. 51)
- **Stage layout suggestions** based on venue dimensions and contestant count
- **Schedule optimization** that avoids known conflicts

### 11.5 Online Store / Merchandise
- The book mentions monetizing social media (p. 57) and selling program books
- Pageant-branded merchandise store (t-shirts, tote bags, banners)
- Contestant goody bag sponsorship matching

### 11.6 Live Streaming Integration
- Livestream pageant to remote audience (Ticketed?)
- Integrated with Crowd Favorite voting (remote viewers can also vote)
- Video archive for contestant review

### 11.7 Pageant Acquisition / Transition Support
- Book Ch. 2 p. 14 discusses purchasing an existing pageant
- Feature to import/transfer pageant data from one director to another
- Asset inventory: social media accounts, website domains, email lists, intellectual property (logos, systems), sponsor relationships, historical data

### 11.8 Insurance & Bonding Integration
- Event insurance quote/procurement (Ch. 2, p. 16)
- State bond requirement checklists (p. 16)
- Liability waiver generation

### 11.9 Assistant Director Module
- Defined role permissions (see matrix)
- Task delegation (the book discusses when to add an Assistant Director — Ch. 17, p. 149)
- Complementary skills matching (one excels at paperwork, another at contestant relations — p. 149)

### 11.10 Conflict of Interest Engine
- Auto-flag when a sponsor, judge, or vendor has a family member competing
- The book dedicates substantial space to this (Ch. 9, p. 91–92): sponsors should not judge, should not have a competing family member, judges should not accept gifts from contestants
- Rule engine: configurable conflict rules per pageant

---

## 12. Appendices & Book References

### A. Key Book Chapters & Their App Coverage

| Chapter | Book Pages | App Feature(s) |
|---|---|---|
| 1: Introduction | 5–8 | Director mindset, community impact (app values) |
| 2: Strong Beginnings | 9–26 | Pageant creation, naming, mission statement, legalities, payment methods, pageant box, digital files, staffing structure |
| 3: Brand & Image | 46–57 | Logo, slogan, email, website, social media presence, director image |
| 4: Structuring | 27–45 | Age divisions, competition categories, entries, bios, production numbers, stage formations, awards |
| 5: Scheduling | 58–63 | Date selection, conflict checking (2-hour radius), time/venue considerations |
| 6: Venue | 64–72 | Venue assessment, cost analysis, layout, décor, contract failure |
| 7: Judges & Scoring | 73–80 | Judge selection, handbook, tabulator supplies, scoring systems, scoresheet policies |
| 8: Finances | 81–86 | Budgeting (venue, staffing, awards), fundraiser pageants |
| 9: Sponsorships | 87–92 | Sponsor tiers, donations, bartering, conflict of interest |
| 10: Paperwork | 93–103 | Core documents, digital vs printed, timing strategy, legal/ethical |
| 11: Marketing | 104–108 | Word-of-mouth, social media, email/SMS, countdowns, titleholder leveraging |
| 12: Program Book | 109–114 | Ad sales, design, printing, distribution |
| 13: Pageant Day | 115–126 | Pre-arrival, check-in, judges, backstage, running the show, crowning, photos |
| 14: After Curtains | 127–130 | Paperwork security, staff debrief, sponsor thank-yous, social media wrap-up |
| 15: Titleholders | 131–136 | Active vs one-and-done, expectations, communication, point systems, title removal |
| 16: Handling Negative | 137–146 | Criticism response, being copied, title removal procedures |
| 17: Longevity | 147–153 | Assistant director, vendors, networking, director reflection |
| 18: Beyond Chair | 154–165 | Exit strategy, succession planning, legacy |
| 19: Last But Not Least | 166–174 | Glossary, PDR Shop resources |

### B. Glossary (from Book, p. 172–173)
Integrated terms: Admission, Age Division, Contestant, Crowd Favorite, Director's Discretion, Emcee, Front of House, Head Judge, Hobby Pageant, People's Choice/Crowd Favorite, Photogenic Competition, Program Book, Representative Pageant, Rehearsal, Royalty, Runner-Up, Sponsorship Packet, Tabulator, Themed Wear, Titleholder, Titleholder Contract, Transparency, Volunteer, Walk Pattern — all of these are directly mapped to entities, fields, or documentation in the application.

### C. Resource URLs
- **Pageant Director Resource**: www.PageantDirectorResource.com
- **PDR Shop**: Available through the same site (templates for judge handbooks, staff handbooks, emcee scripts, contestant bio forms, program books, score sheets)
- **Email Contact**: PageantDirectorResource@gmail.com

---

## Document Status

**Version:** 1.0  
**Author:** Generated from *Directing Pageants: A Master Guide* (42,000-word text, 175 pages)  
**License:** This specification is derived from the content of the book. The book is Copyright © 2026 by Tamsyn J. Simon. All rights reserved. This spec is intended for development reference purposes in service of the book's methodology.
