from typing import List
from pydantic import BaseModel
from app.modules.transformer.engine.resolver import resolve_value_from_path
from app.modules.transformer.engine.transformers import (
    evaluate_condition,
    mask_data,
    transform_data,
)
from app.modules.transformer.engine.validators import validate_required_fields
from app.modules.transformer.error_collector import ErrorCodes, ErrorCollector
from app.modules.transformer.schema import (
    JSONValue,
    MaskTypes,
    TransformTemplateSchema,
    TransformTypes,
    ValidationSchema,
)
import logging

logger = logging.getLogger(__name__)


class ExecutorOutput(BaseModel):
    transformed_payload: JSONValue


def execute_transform(
    payload: JSONValue,
    transform_template: TransformTemplateSchema,
    errors: ErrorCollector,
) -> ExecutorOutput:
    output: dict[str, JSONValue] = {}

    for key, value in transform_template.output.items():

        if value.value is not None:
            output[key] = value.value
            continue

        if value.condition is not None:
            output[key] = evaluate_condition(value.condition, payload, errors)
            continue

        if value.object is not None:
            nested_template = TransformTemplateSchema(output=value.object)
            result = execute_transform(payload, nested_template, errors)
            output[key] = result.transformed_payload
            continue

        if value.map is not None:
            path = ""
            default = None

            if value.path is not None:
                path = value.path

            if value.default is not None:
                default = value.default

            resolved_value = resolve_value_from_path(path, payload, errors, default)

            iterable = resolved_value
            item_output: List[JSONValue] = []

            if not isinstance(iterable, list):
                errors.add(
                    code=ErrorCodes.TYPE_MISMATCH,
                    message=f"Value is not a valid type",
                    field="value",
                    path="value",
                    operation="transform_data",
                )
                iterable = []

            nested_template = TransformTemplateSchema(output=value.map)

            for item in iterable:
                result = execute_transform(item, nested_template, errors)
                item_output.append(result.transformed_payload)

            output[key] = item_output
            continue

        path = ""
        default = None

        if value.path is not None:
            path = value.path

        if value.default is not None:
            default = value.default

        resolved_value = resolve_value_from_path(path, payload, errors, default)

        if value.transform is not None:
            transform_type = value.transform
            if transform_type is not None and transform_type in TransformTypes:
                resolved_value = transform_data(resolved_value, transform_type, errors)
            else:
                errors.add(
                    code=ErrorCodes.INVALID_TRANSFORM,
                    message=f"Invalid transform type: {transform_type}",
                    field="transform",
                    path="transform",
                    operation="transform_data",
                )
                resolved_value = None

        if value.mask is not None:
            if not isinstance(resolved_value, str):
                errors.add(
                    code=ErrorCodes.TYPE_MISMATCH,
                    message=f"Value is not a valid type",
                    field="value",
                    path="value",
                    operation="mask_data",
                )

            mask_type = value.mask
            if mask_type is not None and mask_type in MaskTypes:
                resolved_value = mask_data(resolved_value, errors, mask_type)
            else:
                errors.add(
                    code=ErrorCodes.INVALID_MASK,
                    message=f"Invalid mask type: {mask_type}",
                    field="mask",
                    path="mask",
                    operation="transform_data",
                )

        output[key] = resolved_value

    return ExecutorOutput(transformed_payload=output)


def execute_validation(
    payload: JSONValue,
    schema: ValidationSchema,
    errors: ErrorCollector,
    path: str = "payload",
):
    logger.info(f"Executing validation for path: {path}")
    if payload is None:
        return

    if schema.type == "object":
        if not isinstance(payload, dict):
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                "Payload is not a dictionary",
                path,
                path,
                "validate_required_fields",
            )
            return

        if schema.required is not None:
            validate_required_fields(payload, schema.required, errors, path)

        if schema.properties is not None:
            for key, value in schema.properties.items():
                if key in payload:
                    current = payload[key]
                    execute_validation(current, value, errors, f"{path}.{key}")

    elif schema.type == "array":
        if not isinstance(payload, list):
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                "Payload is not a list",
                path,
                path,
                "validate_required_fields",
            )
            return

        if schema.items is not None:
            for index, item in enumerate(payload):
                execute_validation(item, schema.items, errors, f"{path}[{index}]")

    elif schema.type == "boolean":
        if not isinstance(payload, bool):
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                "Payload is not a boolean",
                path,
                path,
                "validate_required_fields",
            )

    elif schema.type == "string":
        if not isinstance(payload, str):
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                "Payload is not a string",
                path,
                path,
                "validate_required_fields",
            )

    elif schema.type == "number":
        if not isinstance(payload, (int, float)):
            errors.add(
                ErrorCodes.SCHEMA_VALIDATION_ERROR,
                "Payload is not a number",
                path,
                path,
                "validate_required_fields",
            )

    else:
        errors.add(
            ErrorCodes.SCHEMA_VALIDATION_ERROR,
            "Invalid schema type",
            path,
            path,
            "validate_required_fields",
        )
