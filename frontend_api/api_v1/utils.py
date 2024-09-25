from uuid import UUID
from decimal import Decimal
from datetime import datetime, date


def convert_to_serializable(data):
    """
    Recursively converts non-serializable fields like datetime and Decimal to strings.

    Args:
        data (dict, list, or primitive types): The data to process.

    Returns:
        The data with all non-serializable fields converted to strings.
    """
    if isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]

    elif isinstance(data, (datetime, date)):
        return data.isoformat()

    elif isinstance(data, Decimal):
        return str(data)

    elif isinstance(data, UUID):
        return str(data)

    else:
        return data
