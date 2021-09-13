import csv
import logging
import os
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Union

from botocore.client import BaseClient
from gp_file_parser.file_name_parser import validate_filename
from gp_file_parser.utils import pairs
from gp_file_parser.validators import (
    ADDRESS_LINE1_COL,
    ADDRESS_LINE2_COL,
    ADDRESS_LINE3_COL,
    ADDRESS_LINE4_COL,
    ADDRESS_LINE5_COL,
    BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER,
    DOB_COL,
    DRUGS_DISPENSED_MARKER,
    FORENAMES_COL,
    GP_PRACTICECODE_COL,
    HA_CIPHER_COL,
    INVALID,
    INVALID_RECORD,
    INVALID_RECORD_DATA,
    INVALID_RECORD_LEN,
    NHS_NUMBER_COL,
    POSTCODE_COL,
    PREV_SURNAME_COL,
    RECORD_TYPE_1_COL,
    RECORD_TYPE_2_COL,
    RESIDENTIAL_INSTITUTE_CODE,
    RPP_MILEAGE,
    SEX_COL,
    SURNAME_COL,
    TITLE_COL,
    TRANS_DATETIME_COL,
    TRANS_ID_COL,
    VALIDATORS,
    WALKING_UNITS,
)
from jobs.statuses import InputFolderType
from lr_logging.exceptions import InvalidGPExtract, InvalidStructure

LOG = logging.getLogger("listrec")
LOG.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

Columns = Iterable[str]
FileGroup = Iterable[str]
Record = dict[str, Union[str, date, int, float, dict]]
Records = list[Record]
Row = list[str]
RowPair = tuple[str, str]
RowColumns = tuple[list[str], list[str]]

__all__ = [
    "InvalidGPExtract",
    "parse_gp_extract_file",
    "parse_gp_extract_text",
    "parse_gp_extract_file_s3",
    "Records",
    "INVALID",
]

SEP = "~"
RECORD_TYPE = "DOW"
RECORD_1 = "1"
RECORD_2 = "2"


def _validate_record(
    record: Record,
    process_datetime: datetime,
    gp_ha_cipher: str = None,
    other_ids: list[str] = None,
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

    if INVALID in record.keys():
        return record

    validation_errors = {}
    validated_record = {}

    # Apply validator functions mapped to each element, default to string
    # conversion if not defined
    for col, val in record.items():
        # Get validator function for each column and coerce data
        try:
            validator_func = VALIDATORS[col]
        except KeyError:
            raise InvalidStructure(f"Unrecognised column {col}")

        coerced_record, invalid_reason = validator_func(
            val,
            process_datetime=process_datetime,
            gp_ha_cipher=gp_ha_cipher,
            other_ids=other_ids,
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
        InvalidStructure: If any abortive errors are found.
    """

    row_1 = row_pair[0].split(SEP)
    row_2 = row_pair[1].split(SEP)

    trans_datetime = row_1[4] + row_1.pop(5)
    row_1[4] = trans_datetime

    row_1.pop(1)
    row_2.pop(1)

    return row_1 + row_2


def _validate_columns(row_columns: RowColumns):
    for i, (col, val) in enumerate(row_columns):
        if not col and val:
            raise InvalidGPExtract({INVALID_RECORD: INVALID_RECORD_DATA})


def _parse_row_columns(row_pair: RowPair, columns: Columns) -> Record:
    """Convert a row pair and columns into a single record.

    Args:
        row_pair (RowPair): Pair of strings containing row 1 and 2 representing
            a single record from a GP extract.
        columns (Columns): List of column names.

    Returns:
        Record: Dictionary of column names mapped to the row pair
    """

    try:
        row = _parse_row_pair(row_pair)

        if len(columns) != len(row):
            raise InvalidGPExtract({INVALID_RECORD: INVALID_RECORD_LEN})

        row_cols = list(zip(columns, row))

        _validate_columns(row_cols)

        record = dict(row_cols)
        record.pop("", None)

        return record

    except InvalidGPExtract as err:
        record = {INVALID: err.args[0]}

        return record


def parse_gp_extract_text(
    gp_extract_text: str,
    process_datetime: datetime = None,
    gp_ha_cipher: str = None,
) -> Records:
    """Converts text from a GP Extract to records with fieldnames.

    Expects unformatted text containing GP extract records.

    Args:
        gp_extract_text (str): The raw string from GP extract.

        process_datetime (datetime): Time of processing.

        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]

    Raises:
        InvalidStructure: If the file is not a valid extract.
    """

    raw_text = [r.strip() for r in gp_extract_text.split("\n") if r]

    if raw_text[0] != r"503\*":
        raise InvalidStructure(r"Header must be 503\*")

    start_idx = 1

    # Skip column names record if it exists
    if NHS_NUMBER_COL in raw_text[start_idx]:
        start_idx += 2

    columns = [
        RECORD_TYPE_1_COL,
        GP_PRACTICECODE_COL,
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
        RECORD_TYPE_2_COL,
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

    raw_text = list(filter(None, raw_text))

    raw_text.reverse()

    for count, line in enumerate(raw_text):
        if line.endswith("~"):
            raw_text = raw_text[count:]
            break
    else:
        raise InvalidStructure(
            "GP extract does not contain any identifiable DOW records for processing"
        )

    raw_text.reverse()

    ids = []
    validated_records = []

    line_number = start_idx + 1
    for row in pairs(raw_text[start_idx:]):
        validated_record = _validate_record(
            _parse_row_columns(row, columns),
            process_datetime=process_datetime or datetime.now(),
            gp_ha_cipher=gp_ha_cipher,
            other_ids=ids,
        )

        if INVALID in validated_record.keys():
            validated_record[INVALID].update({"ON_LINES": f"{line_number}-{line_number + 1}"})

        validated_records.append(validated_record)

        if TRANS_ID_COL in validated_record.keys():
            ids.append(validated_record[TRANS_ID_COL])

        line_number += 2

    return validated_records


def parse_gp_extract_file(filepath: Path, process_datetime: datetime = None) -> Records:
    """Convert a GP extract file into records with fieldnames.

    Expects unformatted word documents containing GP extract records.

    >>> parse_gp_extract_file('path/to/GPR4LA01.CSA')  # doctest: +SKIP
    [{'RECORD_TYPE': 'DOW', ...}, ...]

    Args:
        filepath (Path): A file paths to the GP extract
            considered to be part of the same extract group.
        gp_ha_cipher (str): GP HA cipher for checking matching patient ciphers.
        process_datetime (datetime): Time of processing.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]

    Raises:
        InvalidStructure: If any abortive errors are found.
        InvalidGPExtract: If any files are not found.
    """

    # Check files exist and are readable

    try:
        with open(filepath):
            pass
    except FileNotFoundError as err:
        raise InvalidGPExtract(str(err).replace("[Errno 2]", "").strip())

    valid_file = validate_filename(os.path.basename(filepath), process_datetime)

    results = parse_gp_extract_text(
        open(filepath).read(),
        process_datetime=process_datetime or datetime.now(),
        gp_ha_cipher=valid_file["ha_cipher"],
    )

    return results


def process_invalid_records(records: Records, include_reason: bool = False) -> tuple[dict, Records]:
    """Filter out valid records from a set of records.

    Optionally include a more informative validation fail reason.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})

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

        out_records.append(record)

    if INVALID in count:
        count.pop(INVALID)

    return dict(count), out_records


def output_records(
    records: Records,
    summary_path: Path,
    include_reason: bool = False,
    invalid_threshold: int = None,
):
    """Create CSV files containing invalids summary and invalid records with reasons.

    Args:
        records (Records): Valid and invalid records to extract invalids from.
        summary_path (Path): Output folder.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})
        invalid_threshold (int): If the number of invalid records is greater than or
            equal to this value, only invalid records are output.
    """

    header = [
        INVALID,
        RECORD_TYPE_1_COL,
        GP_PRACTICECODE_COL,
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
        RECORD_TYPE_2_COL,
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

    count, records = process_invalid_records(records, include_reason=include_reason)

    invalid_count = sum(count.values())

    if invalid_threshold is not None and (invalid_threshold <= invalid_count):
        records = list(filter(lambda x: x.get(INVALID), records))

    for record in records:
        invalid = record.get(INVALID)
        if invalid:
            record[INVALID] = " | ".join(invalid.values())

    if not os.path.isdir(summary_path):
        os.makedirs(summary_path)

    records_path = os.path.abspath(os.path.join(summary_path, "records.csv"))
    with open(records_path, "w", newline="\n") as records_file:
        writer = csv.DictWriter(records_file, header)
        writer.writeheader()
        writer.writerows(records)

    count_dict = [{"COLUMN": k, "COUNT": v} for k, v in count.items()]

    count_path = os.path.abspath(os.path.join(summary_path, "invalid_counts.csv"))
    with open(count_path, "w", newline="\n") as count_file:
        writer = csv.DictWriter(count_file, ["COLUMN", "COUNT"])
        writer.writeheader()
        writer.writerows(count_dict)


def process_gp_extract(
    file_path: Path,
    out_dir: Path,
    include_reason: bool,
    invalid_threshold: int,
    process_datetime: datetime,
):
    """Create CSV files containing invalids summary and invalid records with reasons.

    Args:
        file_path (Path): One file path to a GP extract considered to be part of
            the same extract group.
        out_dir (Path): Output folder.
        include_reason (bool): If true, include a verbose description of
            invalid determination. (default: {False})
        invalid_threshold (int): If the number of invalid records is greater than or
            equal to this value, only invalid records are output.
        process_datetime (datetime): Time of processing.
    """

    records = parse_gp_extract_file(file_path, process_datetime)
    output_records(records, out_dir, include_reason, invalid_threshold)


def parse_gp_extract_file_s3(
    s3: BaseClient,
    bucket_name: str,
    file_key: str,
    process_datetime: datetime = None,
) -> dict:
    """Convert a GP extract file into records with fieldnames.

    Args:
        s3 (BaseClient): boto3 s3 client
        bucket_name (str): s3 bucket name
        file_key (str): s3 object file key
        process_datetime (datetime): Time of processing.

    Returns:
        Records: List of records: [{record1: ...}, {record2: ...}, ...]
    """

    valid_file = validate_filename(file_key.replace(InputFolderType.IN.value, ""), process_datetime)

    file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_data = file_obj["Body"].read()

    results = parse_gp_extract_text(
        file_data.decode("utf-8"),
        process_datetime=process_datetime or datetime.now(),
        gp_ha_cipher=valid_file["ha_cipher"],
    )

    invalid_records = [r for r in results if INVALID in list(r.keys())]

    if invalid_records:
        raise InvalidGPExtract({"total_records": len(results), "invalid_records": invalid_records})

    valid_file.update({"records": results})

    return valid_file
