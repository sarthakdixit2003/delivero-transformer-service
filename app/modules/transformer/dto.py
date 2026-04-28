from app.modules.transformer.error_collector import Error
from pydantic import BaseModel
from typing import List, Dict
from .schema import TransformTemplateSchema, JSONValue


class RuleSchema(BaseModel):
    schema: Dict[str, JSONValue]
    transform_template: TransformTemplateSchema


class TransformRequest(BaseModel):
    payload: Dict[str, JSONValue]
    rule: RuleSchema


class TransformResponse(BaseModel):
    transformed_payload: Dict[str, JSONValue]
    errors: List[Error]
