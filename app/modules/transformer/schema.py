from enum import Enum
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel

type JSONType = (str | int | float | bool | None | list[JSONType] | dict[str, JSONType])

JSONValue = JSONType


class TransformTypes(str, Enum):
    TO_STRING = "to_string"
    TO_NUMBER = "to_number"
    TO_BOOLEAN = "to_boolean"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    TRIM = "trim"


class MaskTypes(str, Enum):
    LAST4 = "last4"
    FULL_MASK = "full_mask"


class OperatorTypes(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"


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


class ValidationSchema(BaseModel):
    type: Literal["string", "number", "boolean", "object", "array"]
    required: Union[List[str], None] = None
    properties: Union[Dict[str, ValidationSchema], None] = None
    items: Optional["ValidationSchema"] = None


# resolve forward refs
OutputSchema.model_rebuild()
ValidationSchema.model_rebuild()
