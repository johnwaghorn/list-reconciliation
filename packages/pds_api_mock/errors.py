from fastapi import status
from pds_api_mock.model import Details, ErrorCoding, ErrorResponse, Issue, IssueDisplay


def error_response_404(patient_id=None):
    try:
        if patient_id:
            code = "INVALIDATED_RESOURCE"
            display = IssueDisplay.INVALIDATED_RESOURCE
        else:
            code = "RESOURCE_NOT_FOUND"
            display = IssueDisplay.RESOURCE_NOT_FOUND
        return ErrorResponse(
            issue=[
                Issue(details=Details(coding=[ErrorCoding(code=code, display=display)]))
            ]
        )
    except Exception as e:
        return error_response_500(str(e))


def error_response_500(error_message):
    code = "SERVER_ERROR"
    display = IssueDisplay.SERVER_ERROR
    return (
        ErrorResponse(
            issue=[
                Issue(
                    severity="warning",
                    details=Details(coding=[ErrorCoding(code=code, display=display)]),
                )
            ],
            diagnostics=error_message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
