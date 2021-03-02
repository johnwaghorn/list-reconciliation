import pytest

from file_name_parser.file_name_parser import (
    InvalidFilename,
    validate_filenames,
)


@pytest.mark.parametrize(
    "filegroup, expect_raise",
    [
        (["GPR4LET1.xxx"], InvalidFilename),
        (["GPR4A9B1.BPA"], False),
        (["GPR4BRF1.C1A", "GPR4BRF1.C1B"], False),
        (["GPR4BRF1.BFB", "GPR4BRF1.BFC"], InvalidFilename),
        (["GPR4BNF1.BFB", "GPR4BRF1.BFC"], InvalidFilename),
        (["GPR4BRF1.BNA", "GPR4BRF1.BNB", "GPR4BRF1.BNC"], False),
        (["GDR4BRF1.BFA", "GDR4BRF1.BFB", "GDR4BRF1.BFC"], InvalidFilename),
        (["GPR4BRF1.ZFA", "GPR4BRF1.ZFB", "GPR4BRF1.ZFC"], InvalidFilename),
        (["GPR4BRF1.DNA", "GPR4BRF1.DNB", "GPR4BRF1.DNC"], InvalidFilename),
        (["GPR4BRF1.ANA", "GPR4BRF1.ANB", "GPR4BRF1.ANC"], InvalidFilename),
    ],
)
def test_validate_filenames(filegroup, expect_raise):
    if expect_raise:
        with pytest.raises(expect_raise):
            validate_filenames(filegroup)
    else:
        validate_filenames(filegroup)
