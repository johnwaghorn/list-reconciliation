import pytest


def test_lambda_handler_runs_successfully_no_errors_thrown(
    create_dynamo_tables, lambda_handler, lambda_context
):
    response = lambda_handler.main({}, lambda_context)

    assert response is not None
    assert response["status"] == "success"
    assert response["message"] == "LR09 Lambda application stopped"

    assert len(response["processed_jobs"]) == 0
    assert len(response["skipped_jobs"]) == 0
    assert len(response["timed_out_jobs"]) == 0


@pytest.mark.xfail(reason="Error table not being written")
def test_lambda_handler_throws_error_handles_correctly(lambda_handler, lambda_context):
    expected_error_message = "Unhandled exception caught in LR09 Lambda"

    with pytest.raises(Exception) as err:
        assert err is not None
        assert err.value.args[0]["message"] == expected_error_message
