from comparison_engine.core import comparison
from comparison_engine.schema import LeftRecord, RightRecord


@comparison("date_of_birth_not_equal")
def date_of_birth_not_equal(left: LeftRecord, right: RightRecord):
    return left["DATE_OF_BIRTH"] != right["DATE_OF_BIRTH"]


@comparison("surname_not_equal")
def surname_not_equal(left: LeftRecord, right: RightRecord):
    return left["SURNAME"].lower() != right["SURNAME"].lower()


@comparison("forenames_not_equal")
def forenames_not_equal(left: LeftRecord, right: RightRecord):
    return left["FORENAMES"].lower() != right["FORENAMES"].lower()


@comparison("title_not_equal")
def title_not_equal(left: LeftRecord, right: RightRecord):
    return left["TITLE"].lower() != right["TITLE"].lower()


@comparison("gender_not_equal")
def gender_not_equal(left: LeftRecord, right: RightRecord):
    return left["GENDER"].lower() != right["GENDER"].lower()


@comparison("address_not_equal")
def address_not_equal(left: LeftRecord, right: RightRecord):
    return left["ADDRESS"].lower() != right["ADDRESS"].lower()


@comparison("postcode_not_equal")
def postcode_not_equal(left: LeftRecord, right: RightRecord):
    return left["POSTCODE"] != right["POSTCODE"]
