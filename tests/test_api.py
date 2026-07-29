"""Comprehensive tests for the Pageantry App API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app.models import Tenant

client = TestClient(app)
HEADERS = {"X-Tenant-ID": "1"}


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables and default tenant before each test."""
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        existing = db.query(Tenant).filter(Tenant.id == 1).first()
        if not existing:
            db.add(Tenant(id=1, name="Test Director", email="test@test.com",
                          password_hash="pass", role="director", is_active=True))
            db.commit()
    finally:
        db.close()
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_pageant():
    r = client.post("/pageants/", json={
        "name": "Spring Festival 2026",
        "slug": "spring-fest-2026",
        "mission_statement": "Community beauty",
        "pageant_type": "representative"
    }, headers=HEADERS)
    assert r.status_code in (200, 201)
    data = r.json()
    assert data["name"] == "Spring Festival 2026"
    assert data["slug"] == "spring-fest-2026"
    assert data["status"] == "draft"
    assert data["tenant_id"] == 1


def test_list_pageants():
    client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    client.post("/pageants/", json={"name": "P2", "slug": "p2"}, headers=HEADERS)
    r = client.get("/pageants/", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_pageant():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.get(f"/pageants/{pid}", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["name"] == "P1"


def test_update_pageant():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.patch(f"/pageants/{pid}", json={"status": "active"}, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_create_age_division():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/divisions", json={
        "name": "Tiny Miss", "min_age": 3, "max_age": 4, "sort_order": 1
    }, headers=HEADERS)
    assert r.status_code in (200, 201)
    assert r.json()["name"] == "Tiny Miss"


def test_list_divisions():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    client.post(f"/pageants/{pid}/divisions", json={"name": "Little Miss", "sort_order": 2}, headers=HEADERS)
    r = client.get(f"/pageants/{pid}/divisions", headers=HEADERS)
    assert len(r.json()) == 2


def test_create_category():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = r.json()["id"]
    r = client.post(f"/pageants/{pid}/divisions/{did}/categories", json={
        "name": "Formalwear", "category_type": "on_stage", "sort_order": 1
    }, headers=HEADERS)
    assert r.status_code in (200, 201)
    assert r.json()["name"] == "Formalwear"


def test_create_judge_panel_with_judges():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/panels", json={
        "name": "Main Panel",
        "judges": [
            {"first_name": "Sarah", "last_name": "Johnson", "email": "sarah@j.com"},
            {"first_name": "Mike", "last_name": "Brown", "email": "mike@b.com"},
        ]
    }, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Main Panel"


def test_list_panels():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/panels", json={"name": "Panel 1", "judges": []}, headers=HEADERS)
    r = client.get(f"/pageants/{pid}/panels", headers=HEADERS)
    assert len(r.json()) == 1


def test_register_contestant():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    divs = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()
    did = divs[0]["id"]
    r = client.post(f"/pageants/{pid}/contestants", json={
        "division_id": did, "first_name": "Emma", "last_name": "Smith", "age": 4
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["first_name"] == "Emma"
    assert r.json()["contestant_number"] == 1


def test_list_contestants():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "A", "last_name": "B"}, headers=HEADERS)
    r = client.get(f"/pageants/{pid}/contestants", headers=HEADERS)
    assert len(r.json()) == 2


def test_check_in():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    r = client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    cid = r.json()["id"]
    r = client.post(f"/contestants/{cid}/check-in", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["status"] == "checked_in"


def test_create_venue():
    r = client.post("/venues", json={
        "name": "Community Center", "address": "123 Main St", "capacity": 300
    })
    assert r.status_code == 201
    assert r.json()["name"] == "Community Center"


def test_list_venues():
    client.post("/venues", json={"name": "V1"})
    client.post("/venues", json={"name": "V2"})
    r = client.get("/venues")
    assert len(r.json()) == 2


def test_get_venue():
    r = client.post("/venues", json={"name": "V1"})
    vid = r.json()["id"]
    r = client.get(f"/venues/{vid}")
    assert r.json()["name"] == "V1"


def test_submit_score():
    # Setup: pageant, division, category, contestant, judge panel
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/divisions/{did}/categories", json={"name": "Formalwear", "sort_order": 1}, headers=HEADERS)
    cat = client.get(f"/pageants/{pid}/divisions/{did}/categories", headers=HEADERS).json()[0]
    jud = client.post(f"/pageants/{pid}/panels", json={"name": "Panel", "judges": [{"first_name": "J", "last_name": "D"}]}, headers=HEADERS).json()
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    con = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()[0]
    panel = client.get(f"/pageants/{pid}/panels", headers=HEADERS).json()[0]
    judge = panel["judges"][0]

    r = client.post(f"/pageants/{pid}/scores", json={
        "contestant_id": con["id"], "judge_id": judge["id"],
        "category_id": cat["id"], "score_value": 9.5, "comment": "Great"
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["score_value"] == 9.5


def test_tabulation():
    # Full tabulation test
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/divisions/{did}/categories", json={"name": "Formalwear", "sort_order": 1}, headers=HEADERS)
    cat = client.get(f"/pageants/{pid}/divisions/{did}/categories", headers=HEADERS).json()[0]
    client.post(f"/pageants/{pid}/panels", json={"name": "Panel", "judges": [{"first_name": "J", "last_name": "D"}]}, headers=HEADERS)
    panel = client.get(f"/pageants/{pid}/panels", headers=HEADERS).json()[0]
    judge = panel["judges"][0]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "A", "last_name": "B"}, headers=HEADERS)
    cons = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()

    # Score contestant 1 higher
    client.post(f"/pageants/{pid}/scores", json={
        "contestant_id": cons[0]["id"], "judge_id": judge["id"],
        "category_id": cat["id"], "score_value": 9.0
    }, headers=HEADERS)
    client.post(f"/pageants/{pid}/scores", json={
        "contestant_id": cons[1]["id"], "judge_id": judge["id"],
        "category_id": cat["id"], "score_value": 7.5
    }, headers=HEADERS)

    r = client.post(f"/pageants/{pid}/tabulate/{did}", headers=HEADERS)
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 2
    assert results[0]["is_winner"] is True
    assert results[0]["rank"] == 1
    assert results[0]["total_score"] > results[1]["total_score"]


def test_get_results():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/divisions/{did}/categories", json={"name": "Formalwear", "sort_order": 1}, headers=HEADERS)
    cat = client.get(f"/pageants/{pid}/divisions/{did}/categories", headers=HEADERS).json()[0]
    client.post(f"/pageants/{pid}/panels", json={"name": "Panel", "judges": [{"first_name": "J", "last_name": "D"}]}, headers=HEADERS)
    panel = client.get(f"/pageants/{pid}/panels", headers=HEADERS).json()[0]
    judge = panel["judges"][0]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    con = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()[0]
    client.post(f"/pageants/{pid}/scores", json={
        "contestant_id": con["id"], "judge_id": judge["id"],
        "category_id": cat["id"], "score_value": 8.0
    }, headers=HEADERS)
    client.post(f"/pageants/{pid}/tabulate/{did}", headers=HEADERS)
    r = client.get(f"/pageants/{pid}/results", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_create_sponsor():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/sponsors", json={
        "business_name": "Local Biz", "contact_name": "John"
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["business_name"] == "Local Biz"


def test_record_donation():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/donations", json={
        "donor_name": "Generous Donor", "amount": 500
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["donor_name"] == "Generous Donor"


def test_create_marketing_campaign():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/campaigns", json={
        "name": "Summer Push", "campaign_type": "social", "budget": 200
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["name"] == "Summer Push"


def test_create_budget_item():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    r = client.post(f"/pageants/{pid}/budget", json={
        "category": "venue", "description": "Venue rental", "estimated_cost": 1500
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["category"] == "venue"


def test_financial_summary():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/budget", json={
        "category": "venue", "description": "Rental", "estimated_cost": 1000, "actual_cost": 950
    }, headers=HEADERS)
    r = client.get(f"/pageants/{pid}/financial-summary", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["total_budgeted"] == 1000
    assert data["total_actual_expenses"] == 950


def test_create_titleholder():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    con = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()[0]
    r = client.post(f"/pageants/{pid}/titleholders", json={
        "contestant_id": con["id"], "title": "Queen", "reign_start_date": "2026-07-01"
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["title"] == "Queen"


def test_log_appearance():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    con = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()[0]
    r = client.post(f"/pageants/{pid}/titleholders", json={
        "contestant_id": con["id"], "title": "Queen", "reign_start_date": "2026-07-01"
    }, headers=HEADERS)
    tid = r.json()["id"]
    r = client.post(f"/titleholders/{tid}/appearances", json={
        "event_name": "Parade", "date": "2026-07-15", "hours_logged": 2.5
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["event_name"] == "Parade"


def test_add_points():
    r = client.post("/pageants/", json={"name": "P1", "slug": "p1"}, headers=HEADERS)
    pid = r.json()["id"]
    client.post(f"/pageants/{pid}/divisions", json={"name": "Tiny Miss", "sort_order": 1}, headers=HEADERS)
    did = client.get(f"/pageants/{pid}/divisions", headers=HEADERS).json()[0]["id"]
    client.post(f"/pageants/{pid}/contestants", json={"division_id": did, "first_name": "E", "last_name": "S"}, headers=HEADERS)
    con = client.get(f"/pageants/{pid}/contestants", headers=HEADERS).json()[0]
    r = client.post(f"/pageants/{pid}/titleholders", json={
        "contestant_id": con["id"], "title": "Queen", "reign_start_date": "2026-07-01"
    }, headers=HEADERS)
    tid = r.json()["id"]
    r = client.post(f"/titleholders/{tid}/points", json={
        "point_value": 10, "reason": "Community service", "category": "community_service"
    }, headers=HEADERS)
    assert r.status_code == 201
    assert r.json()["point_value"] == 10


def test_auth_register():
    r = client.post("/auth/register", json={
        "name": "New Director", "email": "new@test.com", "password": "secret"
    })
    assert r.status_code == 201
    assert r.json()["email"] == "new@test.com"


def test_auth_login():
    client.post("/auth/register", json={
        "name": "New", "email": "new@test.com", "password": "secret"
    })
    r = client.post("/auth/login", json={"email": "new@test.com", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["email"] == "new@test.com"


def test_auth_me():
    r = client.get("/auth/me", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["id"] == 1