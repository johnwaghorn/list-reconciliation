from comparison_engine.core import comparison
from comparison_engine.schema import LeftRecord, RightRecord


@comparison("MN-BR-DB-01")
def date_of_birth_not_equal(left: LeftRecord, right: RightRecord):
    return left["DATE_OF_BIRTH"] != right["DATE_OF_BIRTH"]


@comparison("MN-BR-SN-01")
def surname_not_equal(left: LeftRecord, right: RightRecord):
    return left["SURNAME"] != right["SURNAME"]


@comparison("MN-BR-FN-01")
def forenames_not_equal(left: LeftRecord, right: RightRecord):
    return left["FORENAMES"] != right["FORENAMES"]


@comparison("MN-BR-TL-01")
def title_not_equal(left: LeftRecord, right: RightRecord):
    return left["TITLE"] != right["TITLE"]


@comparison("MN-BR-SX-01")
def gender_not_equal(left: LeftRecord, right: RightRecord):
    return left["GENDER"] != right["GENDER"]


@comparison("MN-BR-AD-01")
def address_not_equal(left: LeftRecord, right: RightRecord):
    return left["ADDRESS"] != right["ADDRESS"]


@comparison("MN-BR-AD-02")
def postcode_not_equal(left: LeftRecord, right: RightRecord):
    return left["POSTCODE"] != right["POSTCODE"]
