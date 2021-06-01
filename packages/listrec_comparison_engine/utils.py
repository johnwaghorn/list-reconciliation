def strip_ws(in_str: str) -> str:
    """Strip multiple consecutive spaces from a string.

    Args:
        in_str (str): Input string.

    Returns:
        str: Output string.

    """

    return " ".join(in_str.split())
