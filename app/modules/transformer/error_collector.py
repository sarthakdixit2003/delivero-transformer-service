from enum import Enum
from typing import List, Union
from pydantic import BaseModel
from app.modules.transformer.schema import JSONValue


class ErrorCodes(str, Enum):
    INVALID_MASK = "INVALID_MASK"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    RULE_VALIDATION_ERROR = "RULE_VALIDATION_ERROR"
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    INVALID_TRANSFORM = "INVALID_TRANSFORM"
    TRANSFORM_ERROR = "TRANSFORM_ERROR"
    INVALID_CONDITION = "INVALID_CONDITION"
    INVALID_ARRAY = "INVALID_ARRAY"
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"

class Error(BaseModel):
    code: ErrorCodes
    message: str
    field: str
    path: str
    operation: str
    value: Union[JSONValue, None] = None

class ErrorCollector:
    def __init__(self):
        self.errors: List[Error] = []

    
    def add(self, code: ErrorCodes, message: str, field: str, path: str, operation: str, value: Union[JSONValue, None]=None):
        self.errors.append(Error(
            code=code,
            message=message,
            field=field,
            path=path,
            operation=operation,
            value=value
        ))


    def extend(self, errors):
        self.errors.extend(errors)


    def get(self):
        return self.errors