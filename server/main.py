"""whendo — main FastAPI server."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.scheduler.engine import SchedulerEngine
from server.api import recipes, runs, health


scheduler = SchedulerEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop the scheduler with the app."""
    await scheduler.start()
    await scheduler.load_recipes_from_disk(settings.recipes_dir)
    yield
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
    uvicorn.run("server.main:app", host="0.0.0.0", port=settings.port, reload=True)
