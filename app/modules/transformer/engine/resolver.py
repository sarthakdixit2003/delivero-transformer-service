import logging
from app.modules.transformer.error_collector import Error, ErrorCodes, ErrorCollector
from app.modules.transformer.schema import JSONValue

logger = logging.getLogger(__name__)

def resolve_value_from_path(path: str, payload: JSONValue, errors: ErrorCollector, default=None) -> JSONValue:
    """
    Resolve a value from a path in a payload.
    Args:
        path: The path to the value.
        payload: The payload to resolve the value from.
        default: The default value to return if the value is not found.
    Returns:
        The value from the path in the payload.
    """
    if not path:
        errors.add(
            code=ErrorCodes.PATH_NOT_FOUND,
            message="Path is required",
            field="path",
            path=path,
            operation="resolve_value_from_path"
        )
        return default

    parts = path.split('.')

    if(parts and parts[0] == 'payload'):
        parts = parts[1:]

    current = payload

    for part in parts:
        if(current is None):
            errors.add(
                code=ErrorCodes.PATH_NOT_FOUND,
                message=f"Value at path {path} is not a valid type",
                field=path,
                path=path,
                operation="resolve_value_from_path"
            )
            return default
        
        if isinstance(current, dict):
            if(part in current):
                current = current[part]
            else:
                errors.add(
                    code=ErrorCodes.PATH_NOT_FOUND,
                    message=f"Key {part} not found in object at path {path}",
                    field=path,
                    path=path,
                    operation="resolve_value_from_path"
                )
                return default
        
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            if(index>=0 and index<len(current)):
                current = current[index]
            else:
                errors.add(
                    code=ErrorCodes.PATH_NOT_FOUND,
                    message=f"Index {index} is out of range for list at path {path}",
                    field=path,
                    path=path,
                    operation="resolve_value_from_path"
                )
                return default
        
        else:
            errors.add(
                code=ErrorCodes.TYPE_MISMATCH,
                message=f"Value at path {path} is not a valid type",
                field=path,
                path=path,
                operation="resolve_value_from_path"
            )
            return default

    return current if current is not None else default
