from typing import Dict, Literal, Optional, Union
from pydantic import BaseModel

TransformTypes = Literal[
    "to_string",
    "to_number",
    "to_boolean",
    "lowercase",
    "uppercase",
    "capitalize_first_letter",
    "trim",
]
MaskTypes = Literal["last4", "full_mask"]
OperatorTypes = Literal["eq", "neq", "gt", "gte", "lt", "lte"]


class ConditionSchema(BaseModel):
    path: str
    operator: OperatorTypes
    value: Union[str, int, float]


class OutputSchema(BaseModel):
    path: Optional[str] = None
    default: Optional[Union[str, int, float, bool, None]] = None
    transform: Optional[TransformTypes] = None
    mask: Optional[MaskTypes] = None
    condition: Optional[ConditionSchema] = None
    value: Optional[Union[str, int, float, bool]] = None

    # nested types
    object: Optional[Dict[str, OutputSchema]] = None
    map: Optional[Dict[str, OutputSchema]] = None


class TransformTemplateSchema(BaseModel):
    output: Dict[str, OutputSchema]
