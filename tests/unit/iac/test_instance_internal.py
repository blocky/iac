from unittest.mock import Mock

from pytest import raises

import iac
import tests.unit.iac.fixtures as fixtures
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG


def test_describe_instances__happy_path_no_instance_name():
    ec2 = Mock()

    ec2.describe_instances.return_value = fixtures.describe_instances_ret_one_instance

    ret = iac.instance.describe_instances(ec2)
    assert ret == fixtures.describe_instances_ret_one_instance

    ec2.describe_instances.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]},
        ]
    )


def test_describe_instances__happy_path_with_instance_name():
    ec2 = Mock()

    ec2.describe_instances.return_value = fixtures.describe_instances_ret_one_instance

    ret = iac.instance.describe_instances(ec2, fixtures.instance_name)
    assert ret == fixtures.describe_instances_ret_one_instance

    ec2.describe_instances.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]},
            {"Name": "tag:Name", "Values": [fixtures.instance_name]},
        ]
    )


def test_describe_instances__cloud_exception():
    ec2 = Mock()

    ec2.describe_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.instance.describe_instances(ec2)
    assert exc_info.value is fixtures.exp_exc

    ec2.describe_instances.assert_called_once_with(
        Filters=[
            {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]},
        ]
    )
