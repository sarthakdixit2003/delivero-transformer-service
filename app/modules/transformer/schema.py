from enum import Enum
from typing import Dict, Literal, Optional, Union
from pydantic import BaseModel, RootModel

type JSONType = (str | int | float | bool | None | list[JSONType] | dict[str, JSONType])

JSONValue = JSONType

# JSONValue.model_rebuild()


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


# resolve forward refs
OutputSchema.model_rebuild()
