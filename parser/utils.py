from typing import Any, List, Generator, Tuple


def pairs(in_list: List[Any]) -> Generator[Tuple[Any], None, None]:
    """Create a pairwise generator from input list.

    Args:
        in_list: List to process.

    Yields:
        Tuple[Any]: A pair of items from the input list.

    >>> in_list = [1, 2, 3, 4, 5, 6]
    >>> list(pairs(in_list))
    [(1, 2), (3, 4), (5, 6)]
    """
    for k, v in zip(in_list[::2], in_list[1::2]):
        yield k, v
