from datetime import datetime


def strip_whitespace(input: str) -> str:
    """Strip multiple consecutive spaces from a string.

    Args:
        input: Input string or list.

    Returns:
        str: Output string.

    """
    if not input:
        return input

    if isinstance(input, list):
        input = " ".join(filter(None, input))

    return str(" ".join(input.split()))


def to_lower(input: str) -> str:
    """Converts String to lowercase
    Args:
        input: Input String

    Returns:
        str: Output String in lowercase
    """

    return str(input).lower()


def gp_dob(input: str) -> str:
    """Format date.
    Args:
        input (str): Input Date of Birth(GP) string.

    Returns:
        str: Date as string in the correct format

    """
    return str(datetime.strptime(input, "%Y%m%d"))


def pds_dob(input: str) -> str:
    """Format date.
    Args:
        input (str): Input Date of Birth(PDS) string.

    Returns:
        str: Date as string in the correct format

    """
    return str(datetime.strptime(input, "%Y-%m-%d"))


def gp_address(input: str) -> str:
    """gp_address"""
    return strip_whitespace(", ".join(filter(None, input)))


def pds_address(input: str) -> str:
    """pds_address"""
    return strip_whitespace(", ".join(input))


def gp_gender(input: str) -> str:
    """gp_gender"""
    return {"1": "male", "2": "female", "9": "unknown", "0": "other"}[str(input)]
