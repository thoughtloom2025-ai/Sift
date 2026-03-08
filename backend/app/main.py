import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Sift API...")
    from app.workers.sync_worker import start_scheduler
    start_scheduler()
    yield
    logger.info("Shutting down Sift API...")
    from app.workers.sync_worker import stop_scheduler
    stop_scheduler()


app = FastAPI(
    title="Sift API",
    description="AI-powered executive function assistant for ADHD users",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth, tasks, integrations, agent, energy, freshstart, analytics, admin  # noqa: E402

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(energy.router, prefix="/api/v1")
app.include_router(freshstart.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "app": "Sift"}
