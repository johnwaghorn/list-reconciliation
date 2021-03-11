import csv
import os

from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Dict, List, Union, Tuple

from listrec.parser.file_name_parser import validate_filenames
from listrec.parser.utils import pairs
from listrec.parser.validators import (
    VALIDATORS,
    INVALID,
    RECORD_TYPE_COL,
    GP_CODE_COL,
    HA_CIPHER_COL,
    TRANS_DATETIME_COL,
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

    trans_datetime = row_1[4] + row_1.pop(5)
    row_1[4] = trans_datetime

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
        TRANS_DATETIME_COL,
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
    filepath_group: FilePathGroup, process_datetime: datetime = None
) -> Records:
    """Convert GP extract files into records with fieldnames.

    Expects unformatted word documents containing GP extract records.

    >>> parse_gp_extract_file_group(('path/to/GPR4LA01.CSA', 'path/to/GPR4LA01.CSA'))  # doctest: +SKIP
    [{'RECORD_TYPE': 'DOW', ...}, ...]

    Args:
        file_group (FilePathGroup): One or more file paths to GP extracts
            considered to be part of the same extract group.

        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.

        process_datetime (datetime): Time of processing.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]

    Raises:
        AssertionError: If any abortive errors are found.
    """

    results = []
    _, gp_ha_cipher = validate_filenames([os.path.basename(f) for f in filepath_group])

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


def process_invalid_records(
    records: Records, include_reason: bool = False, invalids_only=False
) -> Tuple[Dict, Records]:
    """Filter out valid records from a set of records.

    Optionally include a more inormative validation fail reason.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})
        invalids_only (bool): If true, only output invalid records. If false,
            output all records.

    Returns:
        Tuple[Dict, Records]: First item is a dict of {columns: invalid counts},
            second item is a records item, containing only invalid records.
    """

    count = Counter()
    out_records = []
    for record in records:
        invalids = record.get(INVALID, {})
        for col in record.keys():
            count[col] += int(bool(invalids.get(col, {})))
            if invalids:
                if not include_reason:
                    record[INVALID] = {k: k for k in invalids}
                else:
                    record[INVALID] = {k: f"{k} {v}" for k, v in invalids.items()}
        if invalids_only and not invalids:
            continue

        out_records.append(record)

    count.pop(INVALID)

    return dict(count), out_records


def output_records(
    records: Records, summary_path: Path, include_reason: bool = False, invalids_only=False
) -> Tuple[Path, Path]:
    """Create CSV files containing invalids summary and invalid records with reasons.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        summary_path (Path): Output folder.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})
        invalids_only (bool): If true, only output invalid records. If false,
            output all records.

    Returns:
        Tuple[Path, Path]: Paths to output files; first the summary, second is
            the invalid records file.
    """

    header = [
        INVALID,
        RECORD_TYPE_COL,
        GP_CODE_COL,
        HA_CIPHER_COL,
        TRANS_DATETIME_COL,
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

    count, records = process_invalid_records(records, include_reason, invalids_only)

    for record in records:
        if invalid := record.get(INVALID):
            record[INVALID] = " | ".join(invalid.values())

    if not os.path.isdir(summary_path):
        os.makedirs(summary_path)

    with open(os.path.join(summary_path, "invalids.csv"), "w", newline="\n") as invalids_file:
        writer = csv.DictWriter(invalids_file, header)
        writer.writeheader()
        writer.writerows(records)

    count_dict = [{"COLUMN": k, "COUNT": v} for k, v in count.items()]

    with open(os.path.join(summary_path, "invalid_counts.csv"), "w", newline="\n") as count_file:
        writer = csv.DictWriter(count_file, ["COLUMN", "COUNT"])
        writer.writeheader()
        writer.writerows(count_dict)

    return summary_path, count_file