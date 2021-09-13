import re


ACTION_UPDATE_PDS = "Update PDS name with GP name"
ACTION_UPDATE_GP = "Update GP name with PDS name"
ACTION_REQUIRES_VALIDATION = "Further validation required"

FORENAME = "Only forename mismatch"
SURNAME = "Only surname mismatch"
BOTH_NAMES = "Both names mismatched"


def compare_patient_name(
    gp_forename: str, gp_surname: str, pds_givenNames: str, pds_familyName: str
) -> tuple[str, str]:
    """Check for name differences between PDS and GP data and flag data
    for further action.

    Args:
        gp_forename (str): GP forename string.
        gp_surname (str): GP surname string.
        pds_givenNames (str): PDS forename string.
        pds_familyName (str): PDS surname string.

    Returns:
        Tuple[str, str]: Action to be taken, Name item
    """

    surname_match = _check_match(gp_surname, pds_familyName)
    forename_match = _check_match(gp_forename, pds_givenNames)

    valid_gp_names = (_validate_name_case(gp_forename), _validate_name_case(gp_surname))

    valid_pds_names = (
        _validate_name_case(pds_givenNames),
        _validate_name_case(pds_familyName),
    )

    if not surname_match and not forename_match:
        if all(
            [
                _check_match(gp_forename, pds_familyName),
                _check_match(gp_surname, pds_givenNames),
            ]
        ):
            if all(valid_gp_names) and all(valid_pds_names):
                return ACTION_UPDATE_PDS, BOTH_NAMES

        return ACTION_REQUIRES_VALIDATION, BOTH_NAMES

    if surname_match and forename_match:
        if all(valid_gp_names) and not all(valid_pds_names):
            if not _validate_name_case(pds_givenNames) and not _validate_name_case(pds_familyName):
                return ACTION_UPDATE_PDS, BOTH_NAMES

            if _validate_name_case(pds_givenNames) and not _validate_name_case(pds_familyName):
                return ACTION_UPDATE_PDS, SURNAME

            if not _validate_name_case(pds_givenNames) and _validate_name_case(pds_familyName):
                return ACTION_UPDATE_PDS, FORENAME

        if not all(valid_gp_names) and all(valid_pds_names):
            if not _validate_name_case(gp_forename) and not _validate_name_case(gp_surname):
                return ACTION_UPDATE_GP, BOTH_NAMES

            if _validate_name_case(gp_forename) and not _validate_name_case(gp_surname):
                return ACTION_UPDATE_GP, SURNAME

            if not _validate_name_case(gp_forename) and _validate_name_case(gp_surname):
                return ACTION_UPDATE_GP, FORENAME

        return ACTION_REQUIRES_VALIDATION, BOTH_NAMES

    if surname_match and not forename_match:
        if any(
            [
                not gp_forename,
                _check_additional_name_hyphenated(gp_forename, pds_givenNames),
            ]
        ):
            return ACTION_UPDATE_GP, FORENAME

        if any(
            [
                not pds_givenNames,
                _check_match_hyphenated(pds_givenNames, gp_forename),
                _check_match_hyphenated(gp_forename, pds_givenNames),
                _check_additional_name_hyphenated(pds_givenNames, gp_forename),
                _check_additional_name(gp_forename, pds_givenNames),
                _check_additional_name(pds_givenNames, gp_forename),
            ]
        ):
            return ACTION_UPDATE_PDS, FORENAME

        if _check_positional_mismatch(gp_forename, pds_givenNames):
            return ACTION_REQUIRES_VALIDATION, FORENAME

        return ACTION_REQUIRES_VALIDATION, FORENAME

    if forename_match and not surname_match:
        if any(
            [
                not gp_surname,
                _check_match_apostrophe(gp_surname, pds_familyName),
                _check_additional_name_hyphenated(gp_surname, pds_familyName),
                _check_additional_name(gp_surname, pds_familyName),
            ]
        ):
            return ACTION_UPDATE_GP, SURNAME

        if any(
            [
                not pds_familyName,
                _check_match_apostrophe(pds_familyName, gp_surname),
                _check_match_hyphenated(gp_surname, pds_familyName),
                _check_match_hyphenated(pds_familyName, gp_surname),
                _check_positional_mismatch(pds_familyName, gp_surname),
                _check_positional_mismatch(gp_surname, pds_familyName),
                _check_additional_name_hyphenated(pds_familyName, gp_surname),
                _check_additional_name(pds_familyName, gp_surname),
            ]
        ):
            return ACTION_UPDATE_PDS, SURNAME

        return ACTION_REQUIRES_VALIDATION, SURNAME


def _check_match(first: str, second: str) -> bool:
    """Check for a match between two name strings.

    Args:
        first (str): First string containing a name.
        second (str): Second string containing a name.

    Returns:
        bool: True if match found
    """

    return first.lower() == second.lower()


def _check_match_hyphenated(first: str, with_hyphen: str) -> bool:
    """Check for a match between two name strings, with one string
    containing a hyphen.

    Args:
        first (str): First string containing a name.
        with_hyphen (str): Second name string containing a hyphen.

    Returns:
        bool: True if match found
    """

    if first and with_hyphen:
        return first.split() == with_hyphen.split("-")


def _check_match_apostrophe(first: str, with_apostraphe: str) -> bool:
    """Check for a match between two name strings, with one string
    containing an apostrophe.

    Args:
        first (str): First string containing a name.
        with_apostraphe (str): Second name string containing an apostrophe.

    Returns:
        bool: True if match found
    """

    if first and with_apostraphe:
        return first.replace(" ", "") == with_apostraphe.replace("'", "")


def _validate_name_case(name: str) -> bool:
    """Validates that name string has the correct
    letter case.

    Args:
        name (str): Name string.

    Returns:
        bool: True if regex met
    """

    ex = r"^[A-Z][a-z]+$|^[A-Z]'[A-Z][a-z]+$"

    if name:
        names = name.split()

        for n in names:
            split_names = n.split("-")

            for sn in split_names:
                if not re.match(ex, sn):
                    return False

        return True


def _check_positional_mismatch(first: str, additional: str) -> bool:
    """Check that the first name name string exists inside the
    a string containing additional names, anywhere except the first item.

    Args:
        first (str): First string containing a name.
        additional (str): Second string containing additional names.

    Returns:
        bool: True if match found
    """

    if additional:
        return first in additional.split()[1:]


def _check_additional_name(first: str, additional: str) -> bool:
    """Check that one name string matches the first part of
    another name string.

    Args:
        first (str): First string containing a name.
        additional (str): Second string containing additional names.

    Returns:
        bool: True if additional names found
    """

    if additional:
        return first == additional.split()[0]


def _check_additional_name_hyphenated(first: str, additional_hyphenated: str) -> bool:
    """Check that one name string matches the first part of
    another hyphenated name string.

    Args:
        first (str): First string containing a name.
        additional (str): Second string containing additional hyphenated names.

    Returns:
        bool: True if additional hyphenated names found
    """

    if additional_hyphenated:
        return first == additional_hyphenated.split("-")[0]
