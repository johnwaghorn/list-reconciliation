from listrec_comparison_engine.comparison_rules.compare_name import (
    ACTION_REQUIRES_VALIDATION,
    ACTION_UPDATE_GP,
    ACTION_UPDATE_PDS,
    BOTH_NAMES,
    FORENAME,
    SURNAME,
    compare_patient_name,
)


def test_compare_patient_name_no_match_require_validation():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "John"
    pds_familyName = "Wilks"

    expected = ACTION_REQUIRES_VALIDATION, BOTH_NAMES

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_forename_mismatch_require_validation():
    gp_forename = "Simon"
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_REQUIRES_VALIDATION, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_surname_mismatch_require_validation():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = "Wilks"

    expected = ACTION_REQUIRES_VALIDATION, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_lower_case_update_gp():
    gp_forename = "peter"
    gp_surname = "smith"
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_GP, BOTH_NAMES

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_lower_case_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "peter"
    pds_familyName = "smith"

    expected = ACTION_UPDATE_PDS, BOTH_NAMES

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_forname_lower_case_additional_update_pds():
    gp_forename = "peter"
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_GP, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_surname_lower_case_additional_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = "smith"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_mixed_lower_case_require_validation():
    gp_forename = "Peter"
    gp_surname = "smith"
    pds_givenNames = "peter"
    pds_familyName = "Smith"

    expected = ACTION_REQUIRES_VALIDATION, BOTH_NAMES

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_missing_gp_surname_update_gp():
    gp_forename = "Peter"
    gp_surname = ""
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_GP, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_missing_pds_surname_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = ""

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_missing_gp_forename_update_gp():
    gp_forename = ""
    gp_surname = "Smith"
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_GP, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_missing_pds_forename_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = ""
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_forename_positional_mismatch_require_validation():
    gp_forename = "Peter"
    gp_surname = "Smith"
    pds_givenNames = "Francis Peter"
    pds_familyName = "Smith"

    expected = ACTION_REQUIRES_VALIDATION, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_surname_positional_mismatch_update_PDS():
    gp_forename = "Mark"
    gp_surname = "Rich Coleman"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_surname_positional_mismatch_update_PDS():
    gp_forename = "Mark"
    gp_surname = "Coleman"
    pds_givenNames = "Mark"
    pds_familyName = "Rich Coleman"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_double_barelled_forename_update_gp():
    gp_forename = "Mark"
    gp_surname = "Coleman"
    pds_givenNames = "Mark-Rich"
    pds_familyName = "Coleman"

    expected = ACTION_UPDATE_GP, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_double_barelled_forename_update_gp():
    gp_forename = "Mark-Rich"
    gp_surname = "Coleman"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_double_barelled_forename_match_update_pds():
    gp_forename = "Peter-Jones"
    gp_surname = "Smith"
    pds_givenNames = "Peter Jones"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_double_barelled_forename_match_update_pds():
    gp_forename = "Peter Jones"
    gp_surname = "Smith"
    pds_givenNames = "Peter-Jones"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_double_barelled_surname_match_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith-Jones"
    pds_givenNames = "Peter"
    pds_familyName = "Smith Jones"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_double_barelled_surname_match_update_pds():
    gp_forename = "Peter"
    gp_surname = "Smith Jones"
    pds_givenNames = "Peter"
    pds_familyName = "Smith-Jones"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_surname_with_apostraphe_update_pds():
    gp_forename = "Peter"
    gp_surname = "O'Conner"
    pds_givenNames = "Peter"
    pds_familyName = "O Conner"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_surname_with_apostraphe_update_gp():
    gp_forename = "Peter"
    gp_surname = "OConner"
    pds_givenNames = "Peter"
    pds_familyName = "O'Conner"

    expected = ACTION_UPDATE_GP, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_additional_forename_update_pds():
    gp_forename = "Angela"
    gp_surname = "Smith"
    pds_givenNames = "Angela Charlotte"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_additional_forename_update_pds():
    gp_forename = "Angela Charlotte"
    gp_surname = "Smith"
    pds_givenNames = "Angela"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, FORENAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_additional_surname_update_gp():
    gp_forename = "Mark"
    gp_surname = "Coleman"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman Rich"

    expected = ACTION_UPDATE_GP, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_additional_surname_update_pds():
    gp_forename = "Mark"
    gp_surname = "Coleman Rich"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_pds_additional_surname_hyphenated_update_gp():
    gp_forename = "Mark"
    gp_surname = "Coleman"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman-Rich"

    expected = ACTION_UPDATE_GP, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_gp_additional_surname_hyphenated_update_pds():
    gp_forename = "Mark"
    gp_surname = "Coleman-Rich"
    pds_givenNames = "Mark"
    pds_familyName = "Coleman"

    expected = ACTION_UPDATE_PDS, SURNAME

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual


def test_compare_patient_name_switched_names_update_pds():
    gp_forename = "Smith"
    gp_surname = "Peter"
    pds_givenNames = "Peter"
    pds_familyName = "Smith"

    expected = ACTION_UPDATE_PDS, BOTH_NAMES

    actual = compare_patient_name(gp_forename, gp_surname, pds_givenNames, pds_familyName)

    assert expected == actual
