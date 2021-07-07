import pytest
from moto import mock_dynamodb2
from pynamodb.exceptions import ScanError

from utils.database.models import Errors


def test_lambda_handler_runs_successfully_no_errors_thrown(
    create_dynamo_tables, lambda_handler, lambda_context
):

    expected_message = {"message": "Lambda application stopped"}
    response = lambda_handler.main({}, lambda_context)
    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "Scheduled checked successfully completed."

    assert len(response["processed_jobs"]) == 0
    assert len(response["skipped_jobs"]) == 0


@pytest.mark.xfail(reason="Error table not being written")
def test_lambda_handler_throws_error_handles_correctly(lambda_handler, lambda_context):
    expected_error_message = "Unhandled error when running the scheduled check"

    with pytest.raises(Exception) as err:
        with mock_dynamodb2():
            Errors.create_table()

            lambda_handler.main(None, lambda_context)

            error = Errors.scan()
            first_error = error.next()
            assert first_error is not None
            assert first_error.Id == "99999999-0909-0909-0909-999999999999"
            assert first_error.Name == "UNHANDLED_ERROR"
            assert first_error.Description == expected_error_message

    assert err is not None
    assert isinstance(err.value, ScanError)
    assert err.value.args[0]["message"] == expected_error_message
