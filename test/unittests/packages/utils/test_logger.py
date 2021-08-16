from utils.logger import success, error


def test_success_ok():
    assert success("Custom message", "test_id") == {
        "status": "success",
        "message": "Custom message",
        "internal_id": "test_id",
    }


def test_error_ok():
    assert error("Custom message", "test_id") == {
        "status": "error",
        "message": "Custom message",
        "internal_id": "test_id",
    }
