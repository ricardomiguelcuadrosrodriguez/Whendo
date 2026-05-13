"""Runs API — see the history of executions."""
from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import desc, select

from server.db.connection import get_session
from server.db.schema import Run

router = APIRouter()


@router.get("")
async def list_runs(
    recipe: str | None = Query(default=None, description="Filter by recipe name"),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict]:
    """Most recent runs, newest first."""
    with get_session() as session:
        stmt = select(Run).order_by(desc(Run.started_at)).limit(limit)
        if recipe:
            stmt = stmt.where(Run.recipe_name == recipe)
        rows = session.execute(stmt).scalars().all()

        return [
            {
                "id": r.id,
                "recipe": r.recipe_name,
                "started_at": r.started_at.isoformat(),
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "status": r.status,
                "error": r.error,
                "output": r.output,
            }
            for r in rows
        ]
