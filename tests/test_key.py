from unittest.mock import Mock, patch

from pytest import raises, mark

import iac


class ExpectedUncaughtKeyException(Exception):
    pass


@mark.parametrize("field", ["KeyName", "Tags"])
def test_key__from_aws_key_pair__error_in_structure(field, aws_parrot):
    key_pair = aws_parrot.describe_key_pairs__one_key["KeyPairs"][0]
    del key_pair[field]
    with raises(KeyError):
        iac.Key.from_aws_key_pair(key_pair)


def test_key__from_aws_instance__happy_path(aws_parrot):
    key_pair = aws_parrot.describe_key_pairs__one_key["KeyPairs"][0]
    ret = iac.Key.from_aws_key_pair(key_pair)

    assert ret.name == aws_parrot.key_name
    assert ret.tags == [
        {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
    ]


@patch("builtins.open")
def test_key_file_manager__create__happy_path(mock_open):
    name = "name"
    folder = "folder"
    material = "material"

    path = folder + "/" + name + ".pem"
    want = iac.KeyFile(path=path, username="ec2-user")

    file = Mock()
    mock_open.return_value.__enter__.return_value = file
    file.write.return_value = None

    got = iac.KeyFileManager(folder).create(name, material)
    assert want == got
    mock_open.assert_called_once_with(want.path, mode="x", encoding="utf-8")
    file.write.assert_called_once_with(material)


@patch("os.remove")
def test_key_file_manager__delete__happy_path(mock_remove):
    name = "name"
    folder = "folder"

    path = folder + "/" + name + ".pem"
    want = iac.KeyFile(path=path, username="ec2-user")

    got = iac.KeyFileManager(folder).delete(name)
    assert want == got
    mock_remove.assert_called_once_with(want.path)


@patch("os.remove")
def test_key_file_manager__delete__file_does_not_exist(mock_remove):
    name = "name"
    folder = "folder"

    path = folder + "/" + name + ".pem"
    want = iac.KeyFile(path=path, username="ec2-user")

    mock_remove.side_effect = FileNotFoundError()

    got = iac.KeyFileManager(folder).delete(name)
    assert want == got
    mock_remove.assert_called_once_with(want.path)


def test_key_file_manager__key_file__happy_path():
    name = "name"
    folder = "folder"
    path = folder + "/" + name + ".pem"
    want = iac.KeyFile(path=path, username="ec2-user")

    got = iac.KeyFileManager(folder).key_file(name)
    assert want == got


def test_create_key_pair__happy_path(aws_parrot):
    kfm = Mock()
    ec2 = Mock()

    aws_response = aws_parrot.create_key_pair
    ec2.create_key_pair.return_value = aws_response

    ret = iac.create_key_pair(ec2, kfm, aws_parrot.key_name)
    assert ret.name == aws_parrot.key_name

    ec2.create_key_pair.assert_called_once_with(
        KeyName=aws_parrot.key_name,
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
    kfm.create.assert_called_once_with(
        aws_parrot.key_name,
        aws_response["KeyMaterial"],
    )


def test_create_key_pair__duplicate_key(aws_parrot):
    kfm = Mock()
    ec2 = Mock()

    ec2.create_key_pair.side_effect = aws_parrot.create_key_pair_error

    with raises(iac.IACKeyWarning) as exc_info:
        iac.create_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.KEY_DUPLICATE

    ec2.create_key_pair.assert_called_once_with(
        KeyName=aws_parrot.key_name,
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
    kfm.create.assert_not_called()


def test_create_key_pair__file_create_error(aws_parrot):
    kfm = Mock()
    ec2 = Mock()

    aws_response = aws_parrot.create_key_pair
    ec2.create_key_pair.return_value = aws_response

    want = ExpectedUncaughtKeyException()
    kfm.create.side_effect = want

    with raises(type(want)) as exc_info:
        iac.create_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value is want

    ec2.create_key_pair.assert_called_once_with(
        KeyName=aws_parrot.key_name,
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

    kfm.create.assert_called_once_with(
        aws_parrot.key_name,
        aws_response["KeyMaterial"],
    )


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__happy_path(mock_describe_key_pairs, aws_parrot):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        aws_parrot.describe_key_pairs__one_key,
        iac.IACKeyWarning(error_code=iac.IACErrorCode.KEY_MISSING, message=""),
    ]

    ret = iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert ret.name == aws_parrot.key_name
    assert ret.tags == [{"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG}]

    mock_describe_key_pairs.assert_called_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=aws_parrot.key_name)
    kfm.delete.assert_called_once_with(aws_parrot.key_name)
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__describe_key_pairs_exception(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    want = ExpectedUncaughtKeyException()
    mock_describe_key_pairs.side_effect = want

    with raises(type(want)) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value is want

    mock_describe_key_pairs.assert_called_once_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_not_called()
    kfm.delete.assert_not_called()


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__key_does_not_exist(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = iac.IACKeyWarning(
        iac.IACErrorCode.KEY_MISSING,
        aws_parrot.key_not_found_error,
    )

    with raises(iac.IACKeyWarning) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.KEY_MISSING

    mock_describe_key_pairs.assert_called_once_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_not_called()
    kfm.delete.assert_not_called()


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__not_exactly_one_key_pair_found(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.return_value = aws_parrot.describe_key_pairs__no_keys

    with raises(iac.IACKeyError) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.KEY_MISSING

    mock_describe_key_pairs.assert_called_once_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_not_called()
    kfm.delete.assert_not_called()


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__cloud_delete_exception(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.return_value = aws_parrot.describe_key_pairs__one_key

    want = ExpectedUncaughtKeyException()
    ec2.delete_key_pair.side_effect = want

    with raises(type(want)) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value is want

    mock_describe_key_pairs.assert_called_once_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=aws_parrot.key_name)
    kfm.delete.assert_not_called()


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__cloud_delete_error(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        aws_parrot.describe_key_pairs__one_key,
        aws_parrot.describe_key_pairs__one_key,
    ]

    with raises(iac.IACKeyError) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value.error_code == iac.IACErrorCode.KEY_DELETE_FAIL

    mock_describe_key_pairs.assert_called_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=aws_parrot.key_name)
    kfm.delete.assert_not_called()
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__describe_key_pairs_second_call_exception(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    want = ExpectedUncaughtKeyException()
    mock_describe_key_pairs.side_effect = [
        aws_parrot.describe_key_pairs__one_key,
        want,
    ]

    with raises(type(want)) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value is want

    mock_describe_key_pairs.assert_called_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=aws_parrot.key_name)
    kfm.delete.assert_not_called()
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.describe_key_pairs")
def test_delete_key_pair__file_delete_exception(
    mock_describe_key_pairs,
    aws_parrot,
):
    kfm = Mock()
    ec2 = Mock()

    mock_describe_key_pairs.side_effect = [
        aws_parrot.describe_key_pairs__one_key,
        aws_parrot.describe_key_pairs__no_keys,
    ]

    want = ExpectedUncaughtKeyException()
    kfm.delete.side_effect = want

    with raises(type(want)) as exc_info:
        iac.delete_key_pair(ec2, kfm, aws_parrot.key_name)
    assert exc_info.value is want

    mock_describe_key_pairs.assert_called_with(ec2, aws_parrot.key_name)
    ec2.delete_key_pair.assert_called_once_with(KeyName=aws_parrot.key_name)
    kfm.delete.assert_called_once_with(aws_parrot.key_name)
    assert mock_describe_key_pairs.call_count == 2


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__happy_path_key_exists(
    mock_describe_key_pairs,
    aws_parrot,
):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = aws_parrot.describe_key_pairs__one_key

    ret = iac.list_key_pairs(ec2)
    assert len(ret) == 1
    assert ret[0].name == aws_parrot.key_name
    assert ret[0].tags == [{"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG}]

    mock_describe_key_pairs.assert_called_once_with(ec2)


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__happy_path_no_keys(mock_describe_key_pairs, aws_parrot):
    ec2 = Mock()

    mock_describe_key_pairs.return_value = aws_parrot.describe_key_pairs__no_keys

    ret = iac.list_key_pairs(ec2)
    assert len(ret) == 0

    mock_describe_key_pairs.assert_called_once_with(ec2)


@patch("iac.key.describe_key_pairs")
def test_list_key_pairs__describe_key_pairs_exception(mock_describe_key_pairs):
    ec2 = Mock()

    want = ExpectedUncaughtKeyException()
    mock_describe_key_pairs.side_effect = want

    with raises(type(want)) as exc_info:
        iac.list_key_pairs(ec2)
    assert exc_info.value is want

    mock_describe_key_pairs.assert_called_once_with(ec2)
