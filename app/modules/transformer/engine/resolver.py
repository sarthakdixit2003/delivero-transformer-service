from app.modules.transformer.schema import JSONValue

def resolve_value_from_path(path: str, payload: JSONValue, default=None) -> JSONValue:
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
        return default

    parts = path.split('.')

    if(parts and parts[0] == 'payload'):
        parts = parts[1:]

    current = payload

    for part in parts:
        if(current is None):
            return default
        
        if isinstance(current, dict):
            if(part in current):
                current = current[part]
            else:
                return default
        
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            if(index>=0 and index<len(current)):
                current = current[index]
            else:
                return default
        
        else:
            return default

    return current
