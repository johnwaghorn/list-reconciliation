import csv
import io
from enum import Enum
from typing import Callable, List, Any, Dict

from retrying import retry

from utils.datetimezone import get_datetime_now


class InvalidErrorType(Enum):
    RECORDS = "INVALID_RECORDS"
    STRUCTURE = "INVALID_STRUCTURE"
    FILENAME = "INVALID_FILENAME"


class InputFolderType(Enum):
    IN = "inbound/"
    PASS = "pass/"
    FAIL = "fail/"
    RETRY = "retry/"


class RegistrationType(Enum):
    GP = "OnlyOnGP"
    PDS = "OnlyOnPDS"


def write_to_mem_csv(rows: List[Dict], header: List[str]) -> io.StringIO:
    """Writes a list of rows and header to an in-memory CSV string.

    Args:
        rows (List[Dict]): List of records to add to the CSV.
        header (List[str]): Header to add to the CSV.

    Returns:
        io.StringIO(): CSV string
    """
    stream = io.StringIO(newline=None)
    writer = csv.DictWriter(stream, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

    return stream


def get_registration_filename(practice_code: str, reg_type: RegistrationType) -> str:
    """Generate a registration diffs filename.

    Args:
        practice_code (str): GP practice code.
        reg_type (RegistrationType): Either 'RegistrationType.GP' or 'RegistrationType.PDS'
            indicating which dataset the records added to the file are exclusive to.

    Returns:
        str: Filename containing formatted practice, dataset name and datetime.
    """
    return f'{practice_code}-{reg_type.value}-{get_datetime_now().strftime("%Y%m%d%H%M%S")}.csv'


class ChunkSizeError(Exception):
    pass


def chunk_list(inlist: List[Any], chunk_size: int, sizing_func: Callable) -> List[List[Any]]:
    """Reduce a list of elements to a list of sub-lists, with each sub-list containing
    elements whose size totals no more than `chunk_size`, using `sizing_func` on each element
    to calculate the size required. Elements are evaluated in sequence and no attempt is made
    to optimise the output list into as small a size as possible by searching for
    complementary-sized elements.

    Args:
        inlist (List[Any]): List of elements to chunk.
        chunk_size (int): Max chunk size, using `sizing_func` to evaluate the size of each element.
        sizing_func (callable): Callable to calculate the size of each element.

    Returns:
        List[List[Any]]: List of lists containing elements whose total size is no more
            than `chunk_size`

    Raises:
        ChunkSizeError: If the list element is larger than the maximum chunk size.
    """

    counter = 0
    chunk = []
    chunks = []

    for record in inlist:
        size = sizing_func(record)
        if size > chunk_size:
            raise ChunkSizeError(
                f"Single element {record} is larger than the max chunk size {size} > {chunk_size}"
            )
        if counter + size <= chunk_size:
            counter += size
            chunk.append(record)
        else:
            chunks.append(chunk)

            counter = size
            chunk = [record]

    else:
        chunks.append(chunk)

    return chunks


def retry_func(func: Callable, **kwargs) -> Any:
    """Retries a function using retrying.retry https://pypi.org/project/retrying/.

    Args:
        func (callable): lambda-wrapped function to run.
        **kwargs: Kwargs to pass to the retrying decorator.

    Returns:
        Any: Any expected return value of the function passed.

    Usage:
        result_of_len = retry_func(
            lambda: len('123456'),
            wait_exponential_multiplier=1000,
            wait_exponential_max=10000,
            stop_max_attempt_number=10)

    """

    @retry(**kwargs)
    def wrapper():
        return func()

    return wrapper()
