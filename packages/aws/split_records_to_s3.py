import json
import os
from typing import Any, Callable

import boto3


class ChunkSizeError(Exception):
    pass


def split_records_to_s3(
    records: list[str],
    id_cols: list[str],
    destination_bucket: str,
    source: str,
    max_size: int = 128 * 1024,
):
    """Splits a list of JSON objects into multiple single files, each containing a single JSON
    object. Payload size to trigger the AWS lambda is optional, and defaults to 128kb, minus the
    bytes needed for the json property names.

    Args:
        records (List[str]): List of JSON objects.
        id_cols (List[str]): List of one or more columns present in each record in `records`
            which can be used to generate a compound ID.
        destination_bucket (str): S3 bucket to output JSON files to.
        source (str): Label to identify the source of the files and to facilitate logging.
        max_size (int, optional): Max payload size, default: 128kb max Lambda Event payload size.
    """

    def utf8len(x):
        return len(x.encode("utf-8"))

    lambda_ = boto3.client("lambda", region_name=os.getenv("AWS_REGION"))

    reserved_len = utf8len(
        json.dumps({"records": "", "destination_bucket": "", "id_cols": "", "source": ""})
    )

    chunks = _chunk_list(records, max_size - reserved_len, utf8len)

    for chunk in chunks:
        body = {
            "records": chunk,
            "destination_bucket": destination_bucket,
            "id_cols": id_cols,
            "source": source,
        }

        lambda_.invoke(
            FunctionName=os.getenv("LR_24_SAVE_RECORDS_TO_S3"),
            InvocationType="Event",
            Payload=json.dumps(body),
        )


def _chunk_list(inlist: list[Any], chunk_size: int, sizing_func: Callable) -> list[list[Any]]:
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
