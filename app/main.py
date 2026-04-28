import logging
from fastapi import FastAPI, APIRouter
from app.modules.transformer.router import transformer_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Event Transformer Service",
    version="1.0.0",
)

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    logger.info("Health check endpoint called")
    return {"status": "ok"}

app.include_router(transformer_router, prefix="/transform", tags=["transform"])
app.include_router(router, prefix="/api/v1")
