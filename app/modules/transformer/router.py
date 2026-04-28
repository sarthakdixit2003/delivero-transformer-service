import logging
from fastapi import APIRouter

from app.modules.transformer.service import TransformerService
from .dto import TransformRequest, TransformResponse

logger = logging.getLogger(__name__)
transformer_router = APIRouter()


@transformer_router.post("/", response_model=TransformResponse)
def transformPayload(req: TransformRequest) -> TransformResponse:
    logger.info("Transform payload endpoint called")
    service = TransformerService(req.payload, req.rule)
    return service.transformPayload()
