import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import ALLOWED_ORIGINS
from src.api.chat import router as chat_router
from src.api.whatsapp import router as whatsapp_router
from src.memory.redis_memory import redis_memory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Musing Doc Agent API...")
    await redis_memory.connect()
    yield
    logger.info("Shutting down...")
    await redis_memory.disconnect()


app = FastAPI(
    title="Musing Doc Agent API",
    description="Agente IA conversacional da Musing Doc",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(whatsapp_router)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "musing-doc-agent"}
