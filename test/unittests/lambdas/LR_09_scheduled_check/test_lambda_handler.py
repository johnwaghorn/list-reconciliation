import pytest
from moto import mock_dynamodb2
from pynamodb.exceptions import ScanError
from utils.models import Errors

from lambdas.LR_09_scheduled_check.scheduled_check import lambda_handler

def test_lambda_handler_runs_successfully_no_errors_thrown(
        create_dynamo_tables
):
    empty_response = lambda_handler(None, None)
    assert empty_response is None


def test_lambda_handler_throws_error_handles_correctly():
    expected_error_message = "Unhandled error when running the scheduled check"

    with pytest.raises(Exception) as err:
        with mock_dynamodb2():
            Errors.create_table()

            lambda_handler(None, None)

            error = Errors.JobIdIndex.query("99999999-0909-0909-0909-999999999999")
            first_error = error.next()
            assert first_error is not None
            assert first_error.Name == "UNHANDLED_ERROR"
            assert first_error.Description == expected_error_message

    assert err is not None
    assert isinstance(err.value, ScanError)
    assert err.value.args[0]["message"] == expected_error_message

