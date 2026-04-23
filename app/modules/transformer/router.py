from fastapi import APIRouter
from .dto import TransformRequest, TransformResponse

router = APIRouter()


@router.post("/", response_model=TransformResponse)
def transformPayload(req: TransformRequest) -> TransformResponse:
    return {"transformed_payload": req.payload, "errors": []}
