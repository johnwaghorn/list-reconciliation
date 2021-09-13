Message = dict[str, str]


def success(message: str, internal_id: str) -> Message:
    """Create a success message as a dictionary.

    Args:
        message (str): Message to add.
        internal_id (str): id of lambda logger

    Returns:
        Message
    """

    return {"status": "success", "message": message, "internal_id": internal_id}


def error(message: str, internal_id: str) -> Message:
    """Create an error message as a dictionary.

    Args:
        message (str): Message to add.
        internal_id (str): id of lambda logger

    Returns:
        Message
    """

    return {"status": "error", "message": message, "internal_id": internal_id}
