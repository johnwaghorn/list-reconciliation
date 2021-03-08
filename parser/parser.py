import csv
import os

from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Dict, List, Union, Tuple

from parser.utils import pairs
from parser.validators import (
    VALIDATORS,
    INVALID,
    RECORD_TYPE_COL,
    GP_CODE_COL,
    HA_CIPHER_COL,
    TRANS_DATE_COL,
    TRANS_TIME_COL,
    TRANS_ID_COL,
    NHS_NUMBER_COL,
    SURNAME_COL,
    FORENAMES_COL,
    PREV_SURNAME_COL,
    TITLE_COL,
    SEX_COL,
    DOB_COL,
    ADDRESS_LINE1_COL,
    ADDRESS_LINE2_COL,
    ADDRESS_LINE3_COL,
    ADDRESS_LINE4_COL,
    ADDRESS_LINE5_COL,
    POSTCODE_COL,
    DRUGS_DISPENSED_MARKER,
    RPP_MILEAGE,
    BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,
    WALKING_UNITS,
    RESIDENTIAL_INSTITUTE_CODE,
)

Columns = Iterable[str]
FileGroup = Iterable[str]
FilePathGroup = Iterable[Path]
Record = Dict[str, Union[str, date, int, float, dict]]
Records = List[Record]
Row = List[str]
RowPair = Tuple[str, str]
RowColumns = Tuple[List[str], List[str]]

__all__ = [
    "InvalidGPExtract",
    "parse_gp_extract_file_group",
    "parse_gp_extract_text",
    "FilePathGroup",
    "Records",
    "INVALID",
]

SEP = "~"
RECORD_TYPE = "DOW"
RECORD_1 = "1"
RECORD_2 = "2"


class InvalidGPExtract(Exception):
    pass


def _validate_record(
    record: Record,
    process_datetime: datetime,
    gp_ha_cipher: str = None,
    other_ids: List[str] = None,
) -> Record:
    """Run pre-mapped validation function against a record.

    Args:
        record (Record): Record to validate.
        process_datetime (datetime): Time of processing.
        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.
        other_ids (List[str]): All other record id's seen so far for checking uniqueness.

    Returns:
        Record: Validated record, with an added field containing validation result.
    """

    validation_errors = {}
    validated_record = {}
    # Apply validator functions mapped to each element, default to string
    # conversion if not defined
    for col, val in record.items():
        # Get validator function for each column and coerce data
        try:
            validator_func = VALIDATORS[col]
        except KeyError:
            raise InvalidGPExtract(f"Unrecognised column {col}")

        coerced_record, invalid_reason = validator_func(
            val, process_datetime=process_datetime, gp_ha_cipher=gp_ha_cipher, other_ids=other_ids
        )
        validated_record[col] = coerced_record
        if invalid_reason:
            validation_errors[col] = invalid_reason

    if validation_errors:
        validated_record[INVALID] = validation_errors

    return validated_record


def _parse_row_pair(row_pair: RowPair) -> Row:
    """Convert a row pair into a single row.

    Args:
        row_pair (RowPair): Pair of strings containing row 1 and 2 representing
            a single record from a GP extract.

    Returns:
        Row: List of field contents

    Raises:
        AssertionError: If any abortive errors are found.
    """

    row_1, row_2 = row_pair
    row_1 = row_pair[0].split(SEP)
    row_2 = row_pair[1].split(SEP)
    assert row_1[0] == RECORD_TYPE, f"Row part 1 must start with '{RECORD_TYPE}'"
    assert row_1[1] == RECORD_1, f"Row part 1 must be identified with '{RECORD_1}'"
    assert row_2[0] == RECORD_TYPE, f"Row part 2 must start with '{RECORD_TYPE}'"
    assert row_2[1] == RECORD_2, f"Row part 2 must be identified with '{RECORD_2}'"

    return row_1[2:] + row_2[2:]


def _validate_columns(row_columns: RowColumns):
    for i, (col, val) in enumerate(row_columns):
        assert not (
            not col and val
        ), f"Missing column name must not contain any value; Column: {i}, Value: {val}"


def _parse_row_columns(row_pair: RowPair, columns: Columns) -> Record:
    """Convert a row pair and columns into a single record.

    Args:
        row_pair (RowPair): Pair of strings containing row 1 and 2 representing
            a single record from a GP extract.
        columns (Columns): List of column names.

    Returns:
        Record: Dictionary of column names mapped to the row pair
    """

    row = [RECORD_TYPE] + _parse_row_pair(row_pair)
    assert len(columns) == len(row), "Columns and row must be the same length"

    row_cols = list(zip(columns, row))
    _validate_columns(row_cols)
    record = dict(row_cols)
    record.pop("", None)

    return record


def _validate_file_group(file_group: FileGroup):
    """Validate the filenames in a file group.

    Checks the following rules:
        - All filenames contain a 3-character file extension
        - All filenames are identical up to the penultimate character
        - When grouping the last character of each file extension, the
            result is alphabetically sequential, starting at 'A'

    Args:
        file_group (FileGroup): One or more filenames for GP extracts.

    Raises:
        InvalidGPExtract: Raised when invalid combinations of filenames or
            filenames have disallowed patterns.
    """

    if not all({len(f.split(".")[-1]) == 3 for f in file_group}):
        raise InvalidGPExtract("Filenames must contain a 3-character file extension")

    if len({f[:-1] for f in file_group}) != 1:
        raise InvalidGPExtract("All filenames must be identical up to the penultimate character")

    file_ids = "".join(sorted([f[-1] for f in file_group]))
    if file_ids not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or not file_ids.startswith("A"):
        raise InvalidGPExtract("File extension identifiers must be sequential, starting from 'A'")


def parse_gp_extract_text(
    gp_extract_text: str,
    first: bool = True,
    process_datetime: datetime = None,
    gp_ha_cipher: str = None,
) -> Records:
    """Converts text from a GP Extract to records with fieldnames.

    Expects unformatted text containing GP extract records.

    Args:
        gp_extract_text (str): The raw string from GP extract.

        first (bool): This is the first (or only) set of contents from a GP
            extract file. Setting this flag expects to see the 503 header.

        process_datetime (datetime): Time of processing.

        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]

    Raises:
        AssertionError: If the file is not a valid extract.
    """

    raw_text = [r.strip() for r in gp_extract_text.split("\n") if r]
    if first:
        assert raw_text[0] == "503\\*", "Header must contain 503\\*"
        start_idx = 1
    else:
        start_idx = 0

    # Skip column names record if it exists
    if NHS_NUMBER_COL in raw_text[start_idx]:
        start_idx += 2

    columns = [
        RECORD_TYPE_COL,
        GP_CODE_COL,
        HA_CIPHER_COL,
        TRANS_DATE_COL,
        TRANS_TIME_COL,
        TRANS_ID_COL,
        NHS_NUMBER_COL,
        SURNAME_COL,
        FORENAMES_COL,
        PREV_SURNAME_COL,
        TITLE_COL,
        SEX_COL,
        DOB_COL,
        ADDRESS_LINE1_COL,
        ADDRESS_LINE2_COL,
        ADDRESS_LINE3_COL,
        ADDRESS_LINE4_COL,
        ADDRESS_LINE5_COL,
        POSTCODE_COL,
        DRUGS_DISPENSED_MARKER,
        RPP_MILEAGE,
        BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,
        WALKING_UNITS,
        RESIDENTIAL_INSTITUTE_CODE,
    ]

    ids = []
    validated_records = []

    for row in pairs(raw_text[start_idx:]):
        validated_record = _validate_record(
            _parse_row_columns(row, columns),
            process_datetime=process_datetime or datetime.now(),
            gp_ha_cipher=gp_ha_cipher,
            other_ids=ids,
        )
        validated_records.append(validated_record)
        ids.append(validated_record[TRANS_ID_COL])

    return validated_records


def parse_gp_extract_file_group(
    filepath_group: FilePathGroup,
    first: bool = True,
    process_datetime: datetime = None,
    gp_ha_cipher: str = None,
) -> Records:
    """Convert GP extract files into records with fieldnames.

    Expects unformatted word documents containing GP extract records.

    >>> parse_gp_extract_file_group(('path/to/GPR4LA01.CSA', 'path/to/GPR4LA01.CSA'))  # doctest: +SKIP
    [{'RECORD_TYPE': 'DOW', ...}, ...]

    Args:
        file_group (FilePathGroup): One or more file paths to GP extracts
            considered to be part of the same extract group.

        first (bool): This is the first (or only) set of contents from a GP
            extract file. Setting this flag expects to see the 503 header.
            Only the first file of an extract group should have the header.

        process_datetime (datetime): Time of processing.

        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]

    Raises:
        AssertionError: If any abortive errors are found.
    """

    results = []
    _validate_file_group([os.path.basename(f) for f in filepath_group])
    first = True
    for path in sorted(filepath_group):
        results.extend(
            parse_gp_extract_text(
                open(path, "r").read(),
                first=first,
                process_datetime=process_datetime or datetime.now(),
                gp_ha_cipher=gp_ha_cipher,
            )
        )

        first = False

    return results


def process_invalid_records(records: Records, include_reason: bool = False) -> Tuple[Dict, Records]:
    """Filter out valid records from a set of records.

    Optionally include a more inormative validation fail reason.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})

    Returns:
        Tuple[Dict, Records]: First item is a dict of {columns: invalid counts},
            second item is a records item, containing only invalid records.
    """

    count = Counter()
    invalid_records = []
    for record in records:
        if invalids := record.get(INVALID):
            for col in record.keys():
                count[col] += int(bool(invalids.get(col, {})))
            if not include_reason:
                record[INVALID] = {k: k for k in invalids}
            else:
                record[INVALID] = {k: f"{k} {v}" for k, v in invalids.items()}
            invalid_records.append(record)

    count.pop(INVALID)

    return dict(count), invalid_records


def output_invalid_records(records: Records, summary_path: Path, include_reason: bool = False):
    """Create CSV files containing invalids summary and invalid records with reasons.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        out_file (Path): [description]
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})

    Returns:
        Tuple[Path, Path]: Paths to output files; first the summary, second is
            the invalid records file.
    """

    header = [
        INVALID,
        RECORD_TYPE_COL,
        GP_CODE_COL,
        HA_CIPHER_COL,
        TRANS_DATE_COL,
        TRANS_TIME_COL,
        TRANS_ID_COL,
        NHS_NUMBER_COL,
        SURNAME_COL,
        FORENAMES_COL,
        PREV_SURNAME_COL,
        TITLE_COL,
        SEX_COL,
        DOB_COL,
        ADDRESS_LINE1_COL,
        ADDRESS_LINE2_COL,
        ADDRESS_LINE3_COL,
        ADDRESS_LINE4_COL,
        ADDRESS_LINE5_COL,
        POSTCODE_COL,
        DRUGS_DISPENSED_MARKER,
        RPP_MILEAGE,
        BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,
        WALKING_UNITS,
        RESIDENTIAL_INSTITUTE_CODE,
    ]

    count, invalid_records = process_invalid_records(records, include_reason)

    for invalid_record in invalid_records:
        invalid_record[INVALID] = " | ".join(invalid_record[INVALID].values())

    with open(summary_path, "w") as outfile:
        writer = csv.DictWriter(outfile, header)
        writer.writeheader()
        writer.writerows(invalid_records)

    count_dict = [{"COLUMN": k, "COUNT": v} for k, v in count.items()]

    base_path, ext = os.path.splitext(summary_path)
    with open(f"{base_path}_counts{ext}", "w") as count_path:
        writer = csv.DictWriter(count_path, ["COLUMN", "COUNT"])
        writer.writeheader()
        writer.writerows(count_dict)

    return summary_path, count_path
