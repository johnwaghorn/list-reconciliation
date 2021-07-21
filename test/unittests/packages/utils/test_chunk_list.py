import pytest

from utils import chunk_list, ChunkSizeError


@pytest.mark.parametrize(
    "inlist,chunk_size,sizing_func,expected",
    (
        (
            ["1", "23", "4567", "1234", "123456", "1"],
            7,
            len,
            [["1", "23", "4567"], ["1234"], ["123456", "1"]],
        ),
        (
            ["1", "23", "4567", "1234", "9999", "1", "9999", "2"],
            10000,
            lambda x: int(x),
            [["1", "23", "4567", "1234"], ["9999", "1"], ["9999"], ["2"]],
        ),
    ),
)
def test_chunk_size(inlist, chunk_size, sizing_func, expected):
    actual = chunk_list(inlist, chunk_size, sizing_func)

    assert actual == expected


def test_chunk_size_element_too_large_raises():
    with pytest.raises(ChunkSizeError):
        chunk_list(["12345"], 4, len)
