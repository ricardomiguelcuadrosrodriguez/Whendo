"""whendo — FastAPI server entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api import health, recipes, runs
from server.config import settings
from server.db.connection import init_db
from server.scheduler.engine import SchedulerEngine


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("whendo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise DB + scheduler at startup; tear down at shutdown."""
    logger.info(f"whendo starting (tz={settings.timezone})")

    init_db()

    scheduler = SchedulerEngine()
    app.state.scheduler = scheduler
    await scheduler.start()
    result = await scheduler.load_recipes_from_disk(settings.recipes_dir)
    logger.info(f"Recipes: {result.summary}")

    yield

    logger.info("whendo shutting down")
    await scheduler.shutdown()


app = FastAPI(
    title="whendo",
    description="Tell your computer when to do things. In plain English.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )
