from unittest.mock import Mock, patch

from pytest import raises

import tests.unit.iac.fixtures as fixtures
from .context import iac


@patch("iac.key.create_key_pair_file")
def test_create_key_pair__happy_path(mock_create_key_pair_file):
    ec2 = Mock()

    ec2.create_key_pair.return_value = fixtures.create_key_pair_res_success

    ret = iac.create_key_pair(ec2, fixtures.key_name)
    assert ret.name == fixtures.key_name

    ec2.create_key_pair.assert_called_once_with(
        KeyName=fixtures.key_name,
        KeyType="rsa",
        KeyFormat="pem",
        TagSpecifications=[
            {
                "ResourceType": "key-pair",
                "Tags": [
                    {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
                ],
            },
        ],
    )
    mock_create_key_pair_file.assert_called_once_with(
        fixtures.key_name,
        fixtures.create_key_pair_res_success["KeyMaterial"],
    )


@patch("iac.key.create_key_pair_file")
def test_create_key_pair__duplicate_key(mock_create_key_pair_file):
    ec2 = Mock()

    ec2.create_key_pair.side_effect = fixtures.create_key_pair_exception

    with raises(iac.IACKeyWarning) as exc_info:
        iac.create_key_pair(ec2, fixtures.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.DUPLICATE_KEY

    ec2.create_key_pair.assert_called_once_with(
        KeyName=fixtures.key_name,
        KeyType="rsa",
        KeyFormat="pem",
        TagSpecifications=[
            {
                "ResourceType": "key-pair",
                "Tags": [
                    {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
                ],
            },
        ],
    )
    mock_create_key_pair_file.assert_not_called()


@patch("iac.key.create_key_pair_file")
def test_create_key_pair__file_create_error(mock_create_key_pair_file):
    ec2 = Mock()

    ec2.create_key_pair.return_value = fixtures.create_key_pair_res_success
    mock_create_key_pair_file.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.create_key_pair(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    ec2.create_key_pair.assert_called_once_with(
        KeyName=fixtures.key_name,
        KeyType="rsa",
        KeyFormat="pem",
        TagSpecifications=[
            {
                "ResourceType": "key-pair",
                "Tags": [
                    {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
                ],
            },
        ],
    )

    mock_create_key_pair_file.assert_called_once_with(
        fixtures.key_name,
        fixtures.create_key_pair_res_success["KeyMaterial"],
    )


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__happy_path(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        fixtures.describe_key_pairs_ret_one_key,
        iac.IACKeyWarning(error_code=iac.IACErrorCode.NO_SUCH_KEY, message=""),
    ]

    ret = iac.delete_key_pair(ec2, fixtures.key_name)
    assert ret.name == fixtures.key_name
    assert ret.tags == [{"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG}]

    mock_describe_key_pairs.assert_called_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=fixtures.key_name)
    mock_delete_key_pair_file.assert_called_once_with(fixtures.key_name)
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__describe_key_pairs_exception(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_key_pairs.assert_called_once_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_not_called()
    mock_delete_key_pair_file.assert_not_called()


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__key_does_not_exist(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = iac.IACKeyWarning(
        iac.IACErrorCode.NO_SUCH_KEY,
        fixtures.describe_key_pair_exc_key_not_found,
    )

    with raises(iac.IACKeyWarning) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.NO_SUCH_KEY

    mock_describe_key_pairs.assert_called_once_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_not_called()
    mock_delete_key_pair_file.assert_not_called()


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__not_exactly_one_key_pair_found(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_no_keys

    with raises(iac.IACKeyError) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.NO_SUCH_KEY

    mock_describe_key_pairs.assert_called_once_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_not_called()
    mock_delete_key_pair_file.assert_not_called()


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__cloud_delete_exception(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_one_key
    ec2.delete_key_pair.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_key_pairs.assert_called_once_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=fixtures.key_name)
    mock_delete_key_pair_file.assert_not_called()


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__cloud_delete_error(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        fixtures.describe_key_pairs_ret_one_key,
        fixtures.describe_key_pairs_ret_one_key,
    ]

    with raises(iac.IACKeyError) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.KEY_DELETE_FAIL

    mock_describe_key_pairs.assert_called_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=fixtures.key_name)
    mock_delete_key_pair_file.assert_not_called()
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__describe_key_pairs_second_call_exception(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        fixtures.describe_key_pairs_ret_one_key,
        fixtures.exp_exc,
    ]

    with raises(Exception) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_key_pairs.assert_called_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=fixtures.key_name)
    mock_delete_key_pair_file.assert_not_called()
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.delete_key_pair_file")
@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__file_delete_exception(
    mock_describe_key_pairs,
    mock_delete_key_pair_file,
):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        fixtures.describe_key_pairs_ret_one_key,
        fixtures.describe_key_pairs_ret_no_keys,
    ]
    mock_delete_key_pair_file.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.delete_key_pair(ec2, fixtures.key_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_key_pairs.assert_called_with(ec2, fixtures.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=fixtures.key_name)
    mock_delete_key_pair_file.assert_called_once_with(fixtures.key_name)
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__happy_path_key_exists(mock_describe_key_pairs):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_one_key

    ret = iac.list_key_pairs(ec2)
    assert len(ret) == 1
    assert ret[0].name == fixtures.key_name
    assert ret[0].tags == [{"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG}]

    mock_describe_key_pairs.assert_called_once_with(ec2)


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__happy_path_no_keys(mock_describe_key_pairs):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = fixtures.describe_key_pairs_ret_no_keys

    ret = iac.list_key_pairs(ec2)
    assert len(ret) == 0

    mock_describe_key_pairs.assert_called_once_with(ec2)


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__describe_key_pairs_exception(mock_describe_key_pairs):
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.list_key_pairs(ec2)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_key_pairs.assert_called_once_with(ec2)
