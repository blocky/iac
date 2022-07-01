from unittest.mock import Mock, patch

from pytest import raises

import iac
import tests.unit.iac.fixtures as fixtures
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACErrorCode
from iac.key import IACKeyWarning, IACKeyError


def test_describe_key_pairs__happy_path_no_key_name():
    ec2 = Mock()

    ec2.describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_one_key

    ret = iac.key.describe_key_pairs(ec2)
    assert ret == fixtures.describe_key_pairs_ret_one_key

    ec2.describe_key_pairs.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ]
    )


def test_describe_key_pairs__happy_path_with_key_name():
    ec2 = Mock()

    ec2.describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_one_key

    ret = iac.key.describe_key_pairs(ec2, fixtures.key_name)
    assert ret == fixtures.describe_key_pairs_ret_one_key

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[fixtures.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )


def test_describe_key_pairs__key_not_found():
    ec2 = Mock()

    ec2.describe_key_pairs.side_effect = fixtures.describe_key_pair_exc_key_not_found

    with raises(IACKeyWarning) as exc_info:
        iac.key.describe_key_pairs(ec2, fixtures.key_name)
    assert exc_info.value.error_code == IACErrorCode.NO_SUCH_KEY

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[fixtures.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )


def test_describe_key_pairs__cloud_exception_no_key_name():
    ec2 = Mock()

    ec2.describe_key_pairs.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.key.describe_key_pairs(ec2)
    assert exc_info.value is fixtures.exp_exc

    ec2.describe_key_pairs.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ]
    )


def test_describe_key_pairs__cloud_exception_with_key_name():
    ec2 = Mock()

    ec2.describe_key_pairs.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.key.describe_key_pairs(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[fixtures.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )


@patch("os.path.exists")
@patch("builtins.open")
@patch("iac.key.key_file_name")
def test_create_key_pair_file__happy_path(mock_key_file_name, mock_open, mock_exists):
    key_material = "key-material"
    file = Mock()

    mock_key_file_name.return_value = fixtures.key_file_name
    mock_exists.return_value = False
    mock_open.return_value.__enter__.return_value = file
    file.write.return_value = None

    iac.key.create_key_pair_file(fixtures.key_name, key_material)

    mock_key_file_name.assert_called_once_with(fixtures.key_name)
    mock_exists.assert_called_once()
    mock_open.assert_called_once()
    file.write.assert_called_once_with(key_material)


@patch("os.path.exists")
@patch("builtins.open")
@patch("iac.key.key_file_name")
def test_create_key_pair_file__file_already_exists(mock_key_file_name, mock_open, mock_exists):
    mock_key_file_name.return_value = fixtures.key_file_name
    mock_exists.return_value = True

    with raises(IACKeyError) as exc_info:
        iac.key.create_key_pair_file(fixtures.key_name, None)
    assert exc_info.value.error_code == IACErrorCode.KEY_FILE_EXISTS

    mock_key_file_name.assert_called_once_with(fixtures.key_name)
    mock_exists.assert_called_once()
    mock_open.assert_not_called()


@patch("os.path.exists")
@patch("builtins.open")
@patch("iac.key.key_file_name")
def test_create_key_pair_file__write_fails(mock_key_file_name, mock_open, mock_exists):
    key_material = "key-material"
    file = Mock()

    mock_key_file_name.return_value = fixtures.key_file_name
    mock_exists.return_value = False
    mock_open.return_value.__enter__.return_value = file
    file.write.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.key.create_key_pair_file(fixtures.key_name, key_material)
    assert exc_info.value is fixtures.exp_exc

    mock_key_file_name.assert_called_once_with(fixtures.key_name)
    mock_exists.assert_called_once()
    mock_open.assert_called_once()
    file.write.assert_called_once_with(key_material)


@patch("os.remove")
@patch("iac.key.key_file_name")
def test_delete_key_pair_file__happy_path(mock_key_file_name, mock_remove):
    mock_key_file_name.return_value = fixtures.key_file_name

    iac.key.delete_key_pair_file(fixtures.key_name)

    mock_key_file_name.assert_called_once_with(fixtures.key_name)
    mock_remove.assert_called_once_with(fixtures.key_file_name)


@patch("os.remove")
@patch("iac.key.key_file_name")
def test_delete_key_pair_file__remove_fails(mock_key_file_name, mock_remove):
    mock_key_file_name.return_value = fixtures.key_file_name
    mock_remove.side_effect = FileNotFoundError()

    with raises(IACKeyError) as exc_info:
        iac.key.delete_key_pair_file(fixtures.key_name)
    assert exc_info.value.error_code == IACErrorCode.NO_SUCH_KEY_FILE

    mock_key_file_name.assert_called_once_with(fixtures.key_name)
    mock_remove.assert_called_once_with(fixtures.key_file_name)
