from unittest.mock import Mock

from pytest import raises

import ned
from ned.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from ned.exception import NEDErrorCode
from ned.key import NEDKeyWarning


class ExpectedUncaughtKeyInternalException(Exception):
    pass


def test_describe_key_pairs__happy_path_no_key_name(aws_parrot):
    ec2 = Mock()

    ec2.describe_key_pairs.return_value = aws_parrot.describe_key_pairs__one_key

    ret = ned.key.describe_key_pairs(ec2)
    assert ret == aws_parrot.describe_key_pairs__one_key

    ec2.describe_key_pairs.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ]
    )


def test_describe_key_pairs__happy_path_with_key_name(aws_parrot):
    ec2 = Mock()

    ec2.describe_key_pairs.return_value = aws_parrot.describe_key_pairs__one_key

    ret = ned.key.describe_key_pairs(ec2, aws_parrot.key_name)
    assert ret == aws_parrot.describe_key_pairs__one_key

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[aws_parrot.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )


def test_describe_key_pairs__key_not_found(aws_parrot):
    ec2 = Mock()

    ec2.describe_key_pairs.side_effect = aws_parrot.key_not_found_error

    with raises(NEDKeyWarning) as exc_info:
        ned.key.describe_key_pairs(ec2, aws_parrot.key_name)
    assert exc_info.value.error_code == NEDErrorCode.KEY_MISSING

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[aws_parrot.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )


def test_describe_key_pairs__cloud_exception_no_key_name():
    ec2 = Mock()

    want = ExpectedUncaughtKeyInternalException()
    ec2.describe_key_pairs.side_effect = want

    with raises(type(want)) as exc_info:
        ned.key.describe_key_pairs(ec2)
    assert exc_info.value is want

    ec2.describe_key_pairs.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ]
    )


def test_describe_key_pairs__cloud_exception_with_key_name(aws_parrot):
    ec2 = Mock()

    want = ExpectedUncaughtKeyInternalException()
    ec2.describe_key_pairs.side_effect = want

    with raises(type(want)) as exc_info:
        ned.key.describe_key_pairs(ec2, aws_parrot.key_name)
    assert exc_info.value is want

    ec2.describe_key_pairs.assert_called_once_with(
        KeyNames=[aws_parrot.key_name],
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        ],
    )
