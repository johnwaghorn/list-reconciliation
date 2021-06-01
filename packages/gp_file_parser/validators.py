"""
This module defines validator functions and the mapping for column to those
functions.

Validation rules are taken from HA/GP LINKS - REGISTRATION - GP SYSTEMS
SPECIFICATION section 3.10 OUT-GOING GENERATED DOWNLOAD TRANSACTIONS.

"""
from datetime import datetime, timedelta
import re
from typing import Tuple, Union, List

__all__ = [
    "INVALID",
    "VALIDATORS",
]


RECORD_TYPE_COL = "RECORD_TYPE"
GP_CODE_COL = "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE"
HA_CIPHER_COL = "TRADING_PARTNER_NHAIS_CIPHER"
TRANS_DATETIME_COL = "DATE_OF_DOWNLOAD"
TRANS_TIME_COL = "TIME_OF_DOWNLOAD"
TRANS_ID_COL = "TRANS_ID"
NHS_NUMBER_COL = "NHS_NUMBER"
SURNAME_COL = "SURNAME"
FORENAMES_COL = "FORENAMES"
PREV_SURNAME_COL = "PREV_SURNAME"
TITLE_COL = "TITLE"
SEX_COL = "SEX"
DOB_COL = "DOB"
ADDRESS_LINE1_COL = "ADDRESS_LINE1"
ADDRESS_LINE2_COL = "ADDRESS_LINE2"
ADDRESS_LINE3_COL = "ADDRESS_LINE3"
ADDRESS_LINE4_COL = "ADDRESS_LINE4"
ADDRESS_LINE5_COL = "ADDRESS_LINE5"
POSTCODE_COL = "POSTCODE"
DRUGS_DISPENSED_MARKER = "DRUGS_DISPENSED_MARKER"
RPP_MILEAGE = "RPP_MILEAGE"
BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER = "BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER"
WALKING_UNITS = "WALKING_UNITS"
RESIDENTIAL_INSTITUTE_CODE = "RESIDENTIAL_INSTITUTE_CODE"

INVALID = "_INVALID_"

INVALID_NULL = "must not be null."
INVALID_RECORD_TYPE = "must be 'DOW'."
INVALID_GP_CODE = (
    "must be a 7-digit numeric GMC National GP code and 1-6-digit "
    "alphanumeric Local GP code separated by a comma."
)
INVALID_HA_CIPHER = "must be a 3-digit alphanumeric code and match the GP HA cipher"
INVALID_TRANS_DATETIME = "must be a datetime in the format YYYYMMDDHHMM and be less than 14 days old and not in the future."
INVALID_NHS_NO = "must be a valid NHS number. Max length 10."
INVALID_SURNAME = (
    "must contain only uppercase alphabetic characters and space, apostrophe "
    "or hyphen. Max length 35."
)
INVALID_FORENAME = (
    "must contain only uppercase alphabetic characters and space, apostrophe, "
    "hyphen, comma or full-stop. Max length 35."
)
INVALID_TITLE = (
    "must contain only uppercase alphabetic characters and space, apostrophe "
    "or hyphen. Max length 35."
)
INVALID_SEX = (
    "must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 for Not Specified."
)
INVALID_DATE_OF_BIRTH = "must be a date in past in the format YYYYMMDD."
INVALID_ADDRESS_LINE = (
    "must contain only uppercase alphabetic characters and space, apostrophe, "
    "hyphen, comma or full-stop. Max length 35."
)
INVALID_POSTCODE = (
    "must be in one of the following formats: AN NAA, ANN NAA, AAN NAA, "
    "AANN NAA, ANA NAA, AANA ANA."
)
INVALID_DRUGS_DISPENSED_MARKER = "must be 'Y' or blank."
INVALID_RPP_MILEAGE = "must be between 3 and 50 inclusive."
INVALID_BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER = "must be 'B' or 'S'."
INVALID_WALKING_UNITS = "must be between 3 and 99 inclusive and be divisible by 3."
INVALID_RESIDENTIAL_INSTITUTE_CODE = (
    "must be a 2-character string and valid code for the patients Health Authority."
)
INVALID_TRANS_ID = "must be a unique not-null integer greater than 0."


ValidatedRecord = Tuple[str, Union[str, None]]


def not_null(func):
    """Decorator for identifying not-null inputs to validator functions"""

    def wraps(val, *args, **kwargs):
        if val in (None, ""):
            return None, INVALID_NULL
        else:
            return func(val, *args, **kwargs)

    return wraps


@not_null
def record_type(record_type_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate record type.

    Record type must not null and be 'DOW'.

    Args:
        record_type_val (str): Record type to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if record_type_val != "DOW":
        invalid_reason = INVALID_RECORD_TYPE

    return record_type_val, invalid_reason


@not_null
def gp_code(gp_code_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate GP code.

    Validation rules: Must be a not-null 7-digit numeric GMC National GP code
    and 1-6-digit alphanumeric Local GP code separated by a comma.

    Args:
        gp_code_val (str): GP Code to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if not re.match(r"^([0-9]{7}),([A-Z0-9]{1,6})$", gp_code_val):
        invalid_reason = INVALID_GP_CODE

    return gp_code_val, invalid_reason


@not_null
def ha_cipher(ha_cipher_val: str, gp_ha_cipher: str = None, **kwargs) -> ValidatedRecord:
    """Coerce and validate HA cipher.

    Validation rules: Must be a not-null 3-digit alphanumeric code.

    Args:
        ha_cipher_val (str): HA cipher to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if not re.match(r"^([A-Z0-9]{3})$", ha_cipher_val) or (ha_cipher_val != gp_ha_cipher):
        invalid_reason = INVALID_HA_CIPHER

    return ha_cipher_val, invalid_reason


@not_null
def transaction_datetime(
    transaction_datetime_val: str, process_datetime: datetime = None, **kwargs
):
    """Coerce and validate Transaction datetime.

    Validation rules: Must be a datetime in the format YYYYMMDDHHMM and be less
    than 14 days old and not in the future.

    Args:
        transaction_datetime_val (str): Transaction datetime to validate.
        process_datetime (datetime): Datetime of processing instant.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if len(transaction_datetime_val) != 12:
        invalid_reason = INVALID_TRANS_DATETIME
    else:
        try:
            transaction_datetime_val = datetime.strptime(transaction_datetime_val, "%Y%m%d%H%M")
            
        except ValueError:
            invalid_reason = INVALID_TRANS_DATETIME
        else:
            if (
                transaction_datetime_val < process_datetime - timedelta(days=14)
            ) or transaction_datetime_val > process_datetime:
                invalid_reason = INVALID_TRANS_DATETIME

            transaction_datetime_val = str(transaction_datetime_val)

    return transaction_datetime_val, invalid_reason


def nhs_number(nhs_number_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate NHS Number.

    Validation rules: Must be a valid NHS number. Max length 10.

    Args:
        nhs_number_val (str): NHS Number to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if nhs_number_val in (None, ""):
        nhs_number_val = None
    else:
        try:
            if not re.match(r"^([A-Z0-9\?\/]{1,15})$|^([0-9]{10})$", nhs_number_val):
                invalid_reason = INVALID_NHS_NO
        except TypeError:
            invalid_reason = INVALID_NHS_NO

    return nhs_number_val, invalid_reason


def surname(surname_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate surname.

    Validation rules: Must contain only uppercase alphabetic characters and
    space, apostrophe or hyphen. Max length 35.

    Args:
        surname_val (str): Surname to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if surname_val in (None, ""):
        surname_val = None
    else:
        try:
            if not re.match(r"^([A-Z\s\'\-]{1,35})$", surname_val):
                invalid_reason = INVALID_SURNAME
        except TypeError:
            invalid_reason = INVALID_SURNAME

    return surname_val, invalid_reason


def forename(forename_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate forenames.

    Validation rules: Must contain only uppercase alphabetic characters,
        apostrophe, hyphen, comma or full-stop.

    Args:
        forename_val (str): Forename to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if forename_val in (None, ""):
        forename_val = None
    else:
        try:
            forenames = forename_val.split()

            if forenames:
                for name in forenames:
                    if not re.match(r"^([A-Z\'\-\.,]+)$", name):
                        invalid_reason = INVALID_FORENAME
            else:
                invalid_reason = INVALID_FORENAME
        except (TypeError, AttributeError):
            invalid_reason = INVALID_FORENAME

    return forename_val, invalid_reason


def title(title_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate title.

    Validation rules: Must contain only uppercase alphabetic characters and
    space, apostrophe or hyphen. Max length 35.

    Args:
        title_val (str): Title to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if title_val in (None, ""):
        title_val = None
    else:
        try:
            if not re.match(r"^([A-Z\s\'\-]{1,35})$", title_val):
                invalid_reason = INVALID_TITLE
        except TypeError:
            invalid_reason = INVALID_TITLE

    return title_val, invalid_reason


def sex(sex_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate sex.

    Validation rules: Must be "1" for Male, "2" for Female, "0" for
    Indeterminate/Not Known or "9" for Not Specified.

    Args:
        sex_val (str): Sex to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if sex_val in (None, ""):
        sex_val = None

    elif sex_val not in ("1", "2", "0", "9"):
        invalid_reason = INVALID_SEX
    else:
        sex_val = int(sex_val)

    return sex_val, invalid_reason


def date_of_birth(date_of_birth_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate date of birth.

    Validation rules: Must be a date in past in the format YYYYMMDD.

    Args:
        date_of_birth_val (str): Date of birth to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if date_of_birth_val in (None, ""):
        date_of_birth_val = None

    elif not isinstance(date_of_birth_val, str):
        invalid_reason = INVALID_DATE_OF_BIRTH
    else:
        if len(date_of_birth_val) != 8:
            invalid_reason = INVALID_DATE_OF_BIRTH
        else:
            date_of_birth_val = datetime.strptime(date_of_birth_val, "%Y%m%d").date()
            if date_of_birth_val > datetime.now().date():
                invalid_reason = INVALID_DATE_OF_BIRTH
            date_of_birth_val = str(date_of_birth_val)

    return date_of_birth_val, invalid_reason


def address_line(address_line_val: str, **kwargs) -> ValidatedRecord:  #
    """Coerce and validate address line.

    Validation rules: Must contain only uppercase alphabetic characters and
    space, apostrophe, hyphen, comma or full-stop. Max length 35.

    Args:
        address_line_val (str): Address line to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if address_line_val in (None, ""):
        address_line_val = None
    else:
        try:
            if not re.match(r"^([A-Z0-9\s\'\-\.,]{1,35})$", address_line_val):
                invalid_reason = INVALID_ADDRESS_LINE
        except TypeError:
            invalid_reason = INVALID_ADDRESS_LINE

    return address_line_val, invalid_reason


def postcode(postcode_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate postcode.

    Validation rules: Must be in one of the following formats: AN NAA,
    ANN NAA, AAN NAA, AANN NAA, ANA NAA, AANA ANA.

    Args:
        postcode_val (str): Postcode to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if postcode_val in (None, ""):
        postcode_val = None

    elif not isinstance(postcode_val, str):
        invalid_reason = INVALID_POSTCODE

    elif len(postcode_val.split()) != 2:
        invalid_reason = INVALID_POSTCODE

    return postcode_val, invalid_reason


def drugs_dispensed_marker(drugs_dispensed_marker_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate drugs dispensed marker.

    Validation rules: Must be 'Y' or blank.

    Args:
        drugs_dispensed_marker_val (str): Drugs dispensed marker to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if drugs_dispensed_marker_val in (None, ""):
        drugs_dispensed_marker_val = None
    else:
        if drugs_dispensed_marker_val != "Y":
            invalid_reason = INVALID_DRUGS_DISPENSED_MARKER

    return drugs_dispensed_marker_val, invalid_reason


def rpp_mileage(rpp_mileage_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate RPP mileage.

    Validation rules: Must be between 3 and 50 inclusive.

    Args:
        rpp_mileage_val (str): RPP mileage to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if rpp_mileage_val in (None, ""):
        rpp_mileage_val = None
    else:
        try:
            rpp_mileage_val = int(rpp_mileage_val)
        except (TypeError, ValueError):
            invalid_reason = INVALID_RPP_MILEAGE
        else:
            if not 3 <= rpp_mileage_val <= 50:
                invalid_reason = INVALID_RPP_MILEAGE

    return rpp_mileage_val, invalid_reason


def blocked_route_special_district_marker(blocked_route_special_district_marker_val: str, **kwargs):
    """Coerce and validate blocked route special district marker.

    Validation rules: Must be 'B' or 'S'.

    Args:
        blocked_route_special_district_marker_val (str): Blocked route special district marker to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if blocked_route_special_district_marker_val in (None, ""):
        blocked_route_special_district_marker_val = None
    else:
        if blocked_route_special_district_marker_val not in ("B", "S"):
            invalid_reason = INVALID_BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER

    return blocked_route_special_district_marker_val, invalid_reason


def walking_units(walking_units_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate walking units.

    Validation rules: Must be between 3 and 99 inclusive and be divisible by 3.

    Args:
        walking_units_val (str): Walking units to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if walking_units_val in (None, ""):
        walking_units_val = None
    else:
        try:
            walking_units_val = int(walking_units_val)
        except TypeError:
            invalid_reason = INVALID_WALKING_UNITS
        else:
            if not 3 <= walking_units_val <= 99 or (walking_units_val % 3):
                invalid_reason = INVALID_WALKING_UNITS

    return walking_units_val, invalid_reason


def residential_institute_code(residential_institute_code_val: str, **kwargs) -> ValidatedRecord:
    """Coerce and validate residential institute code.

    Validation rules: Must be a 2-character string and valid code for the
    patients Health Authority.

    Args:
        walking_units_val (str): Residential institute code to validate.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if residential_institute_code_val in (None, ""):
        residential_institute_code_val = None
    else:
        try:
            if not re.match(r"^([A-Z0-9]{2})$", residential_institute_code_val):
                invalid_reason = INVALID_RESIDENTIAL_INSTITUTE_CODE
        except TypeError:
            invalid_reason = INVALID_RESIDENTIAL_INSTITUTE_CODE

    return residential_institute_code_val, invalid_reason


@not_null
def transaction_id(transaction_id_val: str, other_ids: List[int], **kwargs) -> ValidatedRecord:
    """Coerce and validate transaction id.

    Validation rules: Must be a unique not-null 2-character integer greater than 0.

    Args:
        other_ids (List[str]): All other record id's seen so far for checking uniqueness.

    Returns:
        ValidatedRecord: Tuple of coerced value and invalid reason if any.
    """

    invalid_reason = None
    if not re.match(r"^([1-9]{1}[0-9]*)$", str(transaction_id_val)):
        invalid_reason = INVALID_TRANS_ID
    else:
        transaction_id_val = int(transaction_id_val)

    if transaction_id_val in other_ids:
        invalid_reason = INVALID_TRANS_ID

    return transaction_id_val, invalid_reason


# Callables for validating fields
VALIDATORS = {
    RECORD_TYPE_COL: record_type,
    GP_CODE_COL: gp_code,
    HA_CIPHER_COL: ha_cipher,
    TRANS_DATETIME_COL: transaction_datetime,
    TRANS_ID_COL: transaction_id,
    NHS_NUMBER_COL: nhs_number,
    SURNAME_COL: surname,
    FORENAMES_COL: forename,
    PREV_SURNAME_COL: surname,
    TITLE_COL: title,
    SEX_COL: sex,
    DOB_COL: date_of_birth,
    ADDRESS_LINE1_COL: address_line,
    ADDRESS_LINE2_COL: address_line,
    ADDRESS_LINE3_COL: address_line,
    ADDRESS_LINE4_COL: address_line,
    ADDRESS_LINE5_COL: address_line,
    POSTCODE_COL: postcode,
    DRUGS_DISPENSED_MARKER: drugs_dispensed_marker,
    RPP_MILEAGE: rpp_mileage,
    BLOCKED_ROUTE_SPECIAL_DISTRICT_MARKER: blocked_route_special_district_marker,
    WALKING_UNITS: walking_units,
    RESIDENTIAL_INSTITUTE_CODE: residential_institute_code,
}
