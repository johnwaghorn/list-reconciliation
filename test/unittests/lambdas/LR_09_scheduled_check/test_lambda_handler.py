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
