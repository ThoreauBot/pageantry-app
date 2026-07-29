"""Router for judge panels, score entries, tabulation, and results."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models
from app import schemas

router = APIRouter(tags=["scoring"])


def _tenant_id(x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID")) -> int:
    """Extract tenant ID from header, defaulting to 1."""
    return x_tenant_id or 1


# ── Judge Panels ────────────────────────────────────────────────────────


@router.post("/pageants/{pageant_id}/panels", status_code=201)
def create_panel(
    pageant_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Create a new judge panel for a pageant, optionally with inline judges."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    panel = models.JudgePanel(
        name=payload.get("name"),
        pageant_id=pageant_id,
        tenant_id=tenant_id,
    )
    db.add(panel)
    db.flush()

    # Create judges if provided inline
    for j in payload.get("judges", []):
        judge = models.Judge(
            panel_id=panel.id,
            first_name=j.get("first_name", ""),
            last_name=j.get("last_name", ""),
            email=j.get("email"),
            is_head_judge=j.get("is_head_judge", False),
            is_backup=j.get("is_backup", False),
        )
        db.add(judge)

    db.commit()
    db.refresh(panel)
    return panel


@router.get("/pageants/{pageant_id}/panels", response_model=list[schemas.JudgePanelOut])
def list_panels(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """List all judge panels for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    return pageant.judge_panels_via


@router.get("/panels/{panel_id}", response_model=schemas.JudgePanelOut)
def get_panel(
    panel_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Get a single judge panel by ID."""
    panel = (
        db.query(models.JudgePanel)
        .join(models.Pageant)
        .filter(
            models.JudgePanel.id == panel_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not panel:
        raise HTTPException(status_code=404, detail="Judge panel not found")
    return panel


# ── Panel Judges ────────────────────────────────────────────────────────


@router.post("/panels/{panel_id}/judges", response_model=schemas.JudgeOut, status_code=201)
def add_judge_to_panel(
    panel_id: int,
    payload: schemas.JudgeCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Add a judge to a panel."""
    panel = (
        db.query(models.JudgePanel)
        .join(models.Pageant)
        .filter(
            models.JudgePanel.id == panel_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not panel:
        raise HTTPException(status_code=404, detail="Judge panel not found")

    judge = models.Judge(**payload.model_dump(), panel_id=panel_id)
    db.add(judge)
    db.commit()
    db.refresh(judge)
    return judge


@router.delete("/panels/{panel_id}/judges/{judge_id}", status_code=204)
def remove_judge_from_panel(
    panel_id: int,
    judge_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Remove a judge from a panel."""
    panel = (
        db.query(models.JudgePanel)
        .join(models.Pageant)
        .filter(
            models.JudgePanel.id == panel_id,
            models.Pageant.tenant_id == tenant_id,
        )
        .first()
    )
    if not panel:
        raise HTTPException(status_code=404, detail="Judge panel not found")

    judge = (
        db.query(models.Judge)
        .filter(models.Judge.id == judge_id, models.Judge.panel_id == panel_id)
        .first()
    )
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found in this panel")

    db.delete(judge)
    db.commit()
    return None


# ── Score Entries ───────────────────────────────────────────────────────


@router.post("/pageants/{pageant_id}/scores", response_model=schemas.ScoreEntryOut, status_code=201)
def submit_score(
    pageant_id: int,
    payload: schemas.ScoreEntryCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Submit a single score entry for a pageant."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    # Verify contestant belongs to this pageant
    contestant = (
        db.query(models.Contestant)
        .filter(
            models.Contestant.id == payload.contestant_id,
            models.Contestant.pageant_id == pageant_id,
        )
        .first()
    )
    if not contestant:
        raise HTTPException(status_code=404, detail="Contestant not found in this pageant")

    # Verify judge exists
    judge = db.query(models.Judge).filter(models.Judge.id == payload.judge_id).first()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")

    # Verify category exists
    category = (
        db.query(models.CompetitionCategory)
        .filter(models.CompetitionCategory.id == payload.category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Competition category not found")

    score_entry = models.ScoreEntry(
        **payload.model_dump(),
        pageant_id=pageant_id,
    )
    db.add(score_entry)
    db.commit()
    db.refresh(score_entry)
    return score_entry


@router.get("/pageants/{pageant_id}/scores", response_model=list[schemas.ScoreEntryOut])
def list_scores(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
    judge_id: Optional[int] = None,
    category_id: Optional[int] = None,
    contestant_id: Optional[int] = None,
):
    """List score entries for a pageant with optional filters."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    query = db.query(models.ScoreEntry).filter(models.ScoreEntry.pageant_id == pageant_id)

    if judge_id is not None:
        query = query.filter(models.ScoreEntry.judge_id == judge_id)
    if category_id is not None:
        query = query.filter(models.ScoreEntry.category_id == category_id)
    if contestant_id is not None:
        query = query.filter(models.ScoreEntry.contestant_id == contestant_id)

    return query.order_by(models.ScoreEntry.timestamp.desc()).all()


# ── Tabulation ──────────────────────────────────────────────────────────


@router.post("/pageants/{pageant_id}/tabulate/{division_id}", response_model=list[schemas.TabulationResult])
def run_tabulation(
    pageant_id: int,
    division_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
):
    """Run tabulation for a division: aggregate scores and rank contestants.

    Creates a TabulationRun and Result records, then returns ranked results.
    """
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    division = (
        db.query(models.AgeDivision)
        .filter(
            models.AgeDivision.id == division_id,
            models.AgeDivision.pageant_id == pageant_id,
        )
        .first()
    )
    if not division:
        raise HTTPException(status_code=404, detail="Age division not found in this pageant")

    # Get all contestants in this division
    contestants = (
        db.query(models.Contestant)
        .filter(
            models.Contestant.pageant_id == pageant_id,
            models.Contestant.division_id == division_id,
        )
        .all()
    )
    if not contestants:
        raise HTTPException(
            status_code=400,
            detail="No contestants found in this division",
        )

    # Get all categories for this division
    categories = (
        db.query(models.CompetitionCategory)
        .filter(models.CompetitionCategory.division_id == division_id)
        .all()
    )
    if not categories:
        raise HTTPException(
            status_code=400,
            detail="No competition categories found for this division",
        )

    # Aggregate scores per contestant (average across judges per category, then sum)
    results_data = []
    for contestant in contestants:
        total_score = 0.0
        for category in categories:
            scores = (
                db.query(models.ScoreEntry)
                .filter(
                    models.ScoreEntry.contestant_id == contestant.id,
                    models.ScoreEntry.category_id == category.id,
                    models.ScoreEntry.pageant_id == pageant_id,
                )
                .all()
            )
            if scores:
                # Average score across judges for this category, weighted
                avg = sum(s.score_value for s in scores) / len(scores)
                total_score += avg * category.scoring_weight

        results_data.append(
            {
                "contestant_id": contestant.id,
                "contestant_name": f"{contestant.first_name} {contestant.last_name}",
                "division_id": division_id,
                "total_score": total_score,
                "rank": None,
                "is_winner": False,
                "is_runner_up": False,
                "side_awards": {},
            }
        )

    # Sort by total_score descending and assign ranks
    results_data.sort(key=lambda r: r["total_score"] or 0, reverse=True)
    for idx, result in enumerate(results_data):
        result["rank"] = idx + 1

    # Mark winner and runner-up
    if results_data:
        results_data[0]["is_winner"] = True
    if len(results_data) > 1:
        results_data[1]["is_runner_up"] = True

    # Create TabulationRun
    tab_run = models.TabulationRun(
        pageant_id=pageant_id,
        division_id=division_id,
        status="completed",
    )
    db.add(tab_run)
    db.flush()  # get tab_run.id

    # Create Result records
    for rd in results_data:
        result = models.Result(
            tabulation_run_id=tab_run.id,
            contestant_id=rd["contestant_id"],
            division_id=division_id,
            rank=rd["rank"],
            total_score=rd["total_score"],
            is_winner=rd["is_winner"],
            is_runner_up=rd["is_runner_up"],
            side_awards=rd["side_awards"] or {},
        )
        db.add(result)

    db.commit()

    # Return results as TabulationResult schemas
    return [
        schemas.TabulationResult(**rd)
        for rd in results_data
    ]


# ── Results ─────────────────────────────────────────────────────────────


@router.get("/pageants/{pageant_id}/results", response_model=list[schemas.TabulationResult])
def get_results(
    pageant_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(_tenant_id),
    division_id: Optional[int] = None,
):
    """Get the latest tabulation results for a pageant, optionally filtered by division."""
    pageant = (
        db.query(models.Pageant)
        .filter(models.Pageant.id == pageant_id, models.Pageant.tenant_id == tenant_id)
        .first()
    )
    if not pageant:
        raise HTTPException(status_code=404, detail="Pageant not found")

    # Find the latest completed tabulation run
    query = db.query(models.TabulationRun).filter(
        models.TabulationRun.pageant_id == pageant_id,
        models.TabulationRun.status == "completed",
    )
    if division_id is not None:
        query = query.filter(models.TabulationRun.division_id == division_id)

    tab_run = query.order_by(models.TabulationRun.run_timestamp.desc()).first()
    if not tab_run:
        raise HTTPException(status_code=404, detail="No completed tabulation found for this pageant")

    results = (
        db.query(models.Result)
        .filter(models.Result.tabulation_run_id == tab_run.id)
        .order_by(models.Result.rank)
        .all()
    )

    output = []
    for r in results:
        contestant = db.query(models.Contestant).filter(models.Contestant.id == r.contestant_id).first()
        contestant_name = (
            f"{contestant.first_name} {contestant.last_name}"
            if contestant
            else "Unknown"
        )
        output.append(
            schemas.TabulationResult(
                contestant_id=r.contestant_id,
                contestant_name=contestant_name,
                division_id=r.division_id,
                rank=r.rank,
                total_score=r.total_score,
                is_winner=r.is_winner,
                is_runner_up=r.is_runner_up,
                side_awards=r.side_awards or {},
            )
        )

    return output