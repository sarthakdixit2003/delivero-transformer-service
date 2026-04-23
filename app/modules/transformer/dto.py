from pydantic import BaseModel
from typing import Union, List, Dict
from .schema import TransformTemplateSchema

JSONValue = Union[
    str, int, float, bool, None, List["JSONValue"], Dict[str, "JSONValue"]
]


class RuleSchema(BaseModel):
    schema: Dict[str, JSONValue]
    transform_template: TransformTemplateSchema


class TransformRequest(BaseModel):
    payload: Dict[str, JSONValue]
    rule: RuleSchema


class TransformResponse(BaseModel):
    tranformed_payload: Dict[str, JSONValue]
    errors: List[str]
