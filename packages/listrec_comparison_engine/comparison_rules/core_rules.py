from comparison_engine.core import comparison
from comparison_engine.schema import LeftRecord, RightRecord


@comparison("MN-BR-DB-01")
def date_of_birth_not_equal(left: LeftRecord, right: RightRecord):
    return left["DATE_OF_BIRTH"] != right["DATE_OF_BIRTH"]


@comparison("MN-BR-SN-01")
def surname_not_equal(left: LeftRecord, right: RightRecord):
    return left["SURNAME"].lower() != right["SURNAME"].lower()


@comparison("MN-BR-FN-01")
def forenames_not_equal(left: LeftRecord, right: RightRecord):
    return left["FORENAMES"].lower() != right["FORENAMES"].lower()


@comparison("MN-BR-TL-01")
def title_not_equal(left: LeftRecord, right: RightRecord):
    return left["TITLE"].lower() != right["TITLE"].lower()


@comparison("MN-BR-SX-01")
def gender_not_equal(left: LeftRecord, right: RightRecord):
    return left["GENDER"].lower() != right["GENDER"].lower()


@comparison("MN-BR-AD-01")
def address_not_equal(left: LeftRecord, right: RightRecord):
    return left["ADDRESS"].lower() != right["ADDRESS"].lower()


@comparison("MN-BR-AD-02")
def postcode_not_equal(left: LeftRecord, right: RightRecord):
    return left["POSTCODE"] != right["POSTCODE"]
