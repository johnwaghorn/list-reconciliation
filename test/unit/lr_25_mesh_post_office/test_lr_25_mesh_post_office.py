from .conftest import (
    DATA_FILE,
    MOCK_INBOUND_BUCKET,
    MOCK_INBOUND_KEY,
    MOCK_OUTPUT_BUCKET,
    MOCK_OUTPUT_KEY,
)


def test_check_if_open_should_be_open(mesh_post_office_open):
    """
    If the mesh_post_office_open parameter is truthy, we should expect the Post Office to be Open
    """
    response = mesh_post_office_open.check_if_open()
    expected = True
    assert response == expected


def test_check_if_open_should_be_closed(mesh_post_office_closed):
    """
    If the mesh_post_office_open parameter is falsey, we should expect the Post Office to be Closed
    """
    response = mesh_post_office_closed.check_if_open()
    expected = False
    assert response == expected


def test_s3_list_files_in_bucket(mesh_post_office_open):
    """
    Make sure we find the files on a prefix in a bucket, ignoring any "directories (/)"
    """
    response = mesh_post_office_open.s3_list_files_in_bucket(
        MOCK_INBOUND_BUCKET, MOCK_INBOUND_KEY
    )
    assert len(response) == 1
    assert response[0] == f"{MOCK_INBOUND_KEY}/{DATA_FILE}"


def test_get_mesh_messages(mesh_post_office_open):
    """
    Ensure we get the correct list of expected Mesh messages
    """
    response = mesh_post_office_open.get_mesh_messages(
        MOCK_INBOUND_BUCKET, MOCK_INBOUND_KEY
    )
    assert len(response) == 1
    assert response[0] == f"{MOCK_INBOUND_KEY}/{DATA_FILE}"


def test_s3_move_file(s3, mesh_post_office_open):
    """
    Ensure moved files turn up where we expect them to
    """
    mesh_post_office_open.s3_move_file(
        old_bucket=MOCK_INBOUND_BUCKET,
        old_key=f"{MOCK_INBOUND_KEY}/{DATA_FILE}",
        new_bucket=MOCK_OUTPUT_BUCKET,
        new_key=f"{MOCK_OUTPUT_KEY}/{DATA_FILE}",
    )
    response = s3.get_object(
        Bucket=MOCK_OUTPUT_BUCKET, Key=f"{MOCK_OUTPUT_KEY}/{DATA_FILE}"
    )
    assert response["ContentLength"] > 0


def test_get_mesh_messages_second_mapping(mesh_post_office_open_multiple_mappings):
    """
    Ensure we get the correct messages from the second mappings Mesh bucket
    """
    response = mesh_post_office_open_multiple_mappings.get_mesh_messages(
        f"{MOCK_INBOUND_BUCKET}2", f"{MOCK_INBOUND_KEY}2"
    )
    assert len(response) == 1
    assert response[0] == f"{MOCK_INBOUND_KEY}2/{DATA_FILE}"
