from typing import List
from app.modules.transformer.error_collector import Error, ErrorCodes, ErrorCollector
from app.modules.transformer.schema import JSONValue


def validate_required_fields(
    payload: JSONValue, required_fields: List[str], errors: ErrorCollector, path: str
):
    for field in required_fields:
        if field not in payload:
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                f"Field {field} is required",
                field,
                f"{path}.{field}",
                "validate_required_fields",
            )
            continue

        if payload[field] is None:
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                f"Field {field} is required",
                field,
                f"{path}.{field}",
                "validate_required_fields",
            )
