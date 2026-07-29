"""Pageantry App — FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import (
    auth, pageants, contestants, scoring, venues,
    sponsors, marketing, titleholders, finances
)

app = FastAPI(title="Pageantry App")

# ── CORS (allow all origins for local dev) ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(pageants.router)
app.include_router(contestants.router)
app.include_router(scoring.router)
app.include_router(venues.router)
app.include_router(sponsors.router)
app.include_router(marketing.router)
app.include_router(titleholders.router)
app.include_router(finances.router)

# ── Static files ────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Startup ─────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Create default tenant if none exists
    from app.database import SessionLocal
    from app.models import Tenant
    db = SessionLocal()
    try:
        existing = db.query(Tenant).filter(Tenant.id == 1).first()
        if not existing:
            tenant = Tenant(
                id=1,
                name="Default Director",
                email="director@example.com",
                password_hash="password",
                role="director",
                is_active=True,
            )
            db.add(tenant)
            db.commit()
    finally:
        db.close()


# ── Root redirect ───────────────────────────────────────────────────
@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


# ── Health ──────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "app": "Pageantry App"}