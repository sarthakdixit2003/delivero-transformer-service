from typing import Union
from app.modules.transformer.engine.resolver import resolve_value_from_path
from app.modules.transformer.error_collector import Error, ErrorCodes, ErrorCollector
from app.modules.transformer.schema import ConditionSchema, JSONValue, MaskTypes, OperatorTypes, TransformTypes
import logging

logger = logging.getLogger(__name__)

def mask_data(value: JSONValue, errors: ErrorCollector, mask_strategy: MaskTypes = 'last4') -> Union[str, None]:
    """
    Transform the value to a masked string.
    Args:
        value: The value to mask.
        mask_strategy: The strategy to use for masking.
    Returns:
        The masked string.
    """
    if(value is None):
        return None
    if(not isinstance(value, str)):
        errors.add({
            "code": ErrorCodes.TYPE_MISMATCH,
            "message": f"Value is not a valid type",
            "field": "value",
            "path": "value",
            "operation": "mask_data"
        })
        return None
    if(mask_strategy is None or mask_strategy not in MaskTypes):
        errors.add({
            "code": ErrorCodes.INVALID_MASK,
            "message": f"Invalid mask strategy: {mask_strategy}",
            "field": "mask_strategy",
            "path": "mask_strategy",
            "operation": "mask_data"
        })
        return None
    if isinstance(value, int):
        value = str(value)

    length_of_str = len(value)

    if length_of_str<=4 or mask_strategy == "full_mask":
        return "*"*length_of_str
    
    if mask_strategy == "last4":
        return "*"*(length_of_str-4) + value[-4:]

def evaluate_condition(condition: ConditionSchema, payload: JSONValue, errors: ErrorCollector) -> bool:
    """
    Evaluate a condition against a payload.
    Args:
        condition: The condition to evaluate.
        payload: The payload to evaluate the condition against.
    Returns:
        The result of the condition evaluation.
    """
    resolved_value = resolve_value_from_path(condition.path, payload, errors)
    expected_value = condition.value
    operator = condition.operator

    if resolved_value is None or not isinstance(resolved_value, (str, int, float)):
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value at path {condition.path} is not a valid type",
            field=condition.path,
            path=condition.path,
            operation="evaluate_condition"
        )
        return False

    try:
        if operator in {OperatorTypes.GT, OperatorTypes.GTE, OperatorTypes.LT, OperatorTypes.LTE}:
            resolved_value = float(resolved_value)
            expected_value = float(expected_value)
        elif operator in {OperatorTypes.EQ, OperatorTypes.NEQ}:
            if isinstance(resolved_value, str):
                resolved_value = resolved_value.lower()
                expected_value = expected_value.lower()
            elif isinstance(resolved_value, int):
                resolved_value = int(resolved_value)
                expected_value = int(expected_value)
            elif isinstance(resolved_value, float):
                resolved_value = float(resolved_value)
                expected_value = float(expected_value)
            else:
                return False
        else:
            return False
    except (ValueError, TypeError): 
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value at path {condition.path} is not a valid type",
            field=condition.path,
            path=condition.path,
            operation="evaluate_condition"
        )
        return False

    if operator == OperatorTypes.EQ:
        return resolved_value == expected_value
    elif operator == OperatorTypes.NEQ:
        return resolved_value != expected_value
    elif operator == OperatorTypes.GT:
        return resolved_value > expected_value
    elif operator == OperatorTypes.GTE:
        return resolved_value >= expected_value
    elif operator == OperatorTypes.LT:
        return resolved_value < expected_value
    elif operator == OperatorTypes.LTE:
        return resolved_value <= expected_value
    else:
        return False


def to_string(value: JSONValue, errors: ErrorCollector) -> Union[str, None]:
    if(value is None):
        return None
    if(isinstance(value, float)):
        return str(value)
    elif(isinstance(value, bool)):
        return "true" if value else "false"
    elif(isinstance(value, int)):
        return str(value)
    elif(isinstance(value, str)):
        return value
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid type",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

def to_number(value: JSONValue, errors: ErrorCollector) -> Union[int, float, None]:
    if(value is None):
        return None
    if(isinstance(value, float)):
        return value
    elif(isinstance(value, bool)):
        return 1 if value else 0
    elif(isinstance(value, int)):
        return value
    elif(isinstance(value, str)):
        try:
            return float(value)
        except ValueError:
            errors.add(
                code=ErrorCodes.TYPE_MISMATCH,
                message=f"Value is not a valid number",
                field="value",
                path="value",
                operation="transform_data"
            )
            return None
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid type",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

def to_boolean(value: JSONValue, errors: ErrorCollector) -> Union[bool, None]:
    if(value is None):
        return None
    if(isinstance(value, bool)):
        return value
    elif(isinstance(value, float)):
        return value > 0
    elif(isinstance(value, int)):
        return value > 0
    elif(isinstance(value, str)):
        return value == "true"
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid boolean",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

def lowercase(value: JSONValue, errors: ErrorCollector) -> Union[str, None]:
    if(value is None):
        return None
    if(isinstance(value, str)):
        return value.lower()
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid string",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None  

def uppercase(value: JSONValue, errors: ErrorCollector) -> Union[str, None]:
    if(value is None):
        return None
    if(isinstance(value, str)):
        return value.upper()
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid string",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

def trim(value: JSONValue, errors: ErrorCollector) -> Union[str, None]:
    if(value is None):
        return None
    if(isinstance(value, str)):
        return value.strip()
    else:
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid string",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

TRANSFORM_HANDLER = {
    TransformTypes.TO_STRING: to_string,
    TransformTypes.TO_NUMBER: to_number,
    TransformTypes.TO_BOOLEAN: to_boolean,
    TransformTypes.LOWERCASE: lowercase,
    TransformTypes.UPPERCASE: uppercase,
    TransformTypes.TRIM: trim
}

def transform_data(value: JSONValue, transform_type: TransformTypes, errors: ErrorCollector) -> JSONValue:
    if(isinstance(value, dict) or isinstance(value, list)):
        errors.add(
            code=ErrorCodes.TYPE_MISMATCH,
            message=f"Value is not a valid type",
            field="value",
            path="value",
            operation="transform_data"
        )
        return None

    handler = TRANSFORM_HANDLER[transform_type]

    if(handler is None):
        errors.add(
            code=ErrorCodes.INVALID_TRANSFORM,
            message=f"Invalid transform type: {transform_type}",
            field="transform_type",
            path="transform_type",
            operation="transform_data",
            value=value
        )
        return value

    return handler(value, errors)
