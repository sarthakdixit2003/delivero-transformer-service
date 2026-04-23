from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="Event Transformer Service",
    version="1.0.0",
)

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router, prefix="/api/v1")
