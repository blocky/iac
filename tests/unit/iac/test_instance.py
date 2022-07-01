from unittest.mock import Mock, patch

from pytest import raises

import tests.unit.iac.fixtures as fixtures
from .context import iac


@patch("iac.instance.describe_instances")
def test_create_instance__happy_path(mock_describe_instances):
    ec2 = Mock()
    tags = [
        {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
        {"Key": "Name", "Value": fixtures.instance_name},
    ]

    mock_describe_instances.return_value = fixtures.describe_instances_ret_no_instances
    ec2.run_instances.return_value = fixtures.run_instances_res_success

    ret = iac.create_instance(
        ec2,
        fixtures.instance_name,
        fixtures.key_name,
        fixtures.security_group,
    )
    assert ret.name == fixtures.instance_name
    assert ret.id == fixtures.instance_id
    assert ret.key_name == fixtures.key_name
    assert ret.tags == tags

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.run_instances.assert_called_once_with(
        ImageId="ami-08e4e35cccc6189f4",
        MaxCount=1,
        MinCount=1,
        InstanceType="c5a.xlarge",
        KeyName=fixtures.key_name,
        SecurityGroupIds=[fixtures.security_group],
        EnclaveOptions={"Enabled": True},
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": tags,
            },
        ],
    )


@patch("iac.instance.describe_instances")
def test_create_instance__describe_instances_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.create_instance(
            ec2,
            fixtures.instance_name,
            fixtures.key_name,
            fixtures.security_group,
        )
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.run_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_create_instance__instance_already_exists(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_one_instance
    ec2.run_instances.return_value = fixtures.run_instances_res_success

    with raises(iac.IACInstanceWarning) as exc_info:
        iac.create_instance(
            ec2,
            fixtures.instance_name,
            fixtures.key_name,
            fixtures.security_group,
        )
    assert exc_info.value.error_code == iac.IACErrorCode.DUPLICATE_INSTANCE

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.run_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_create_instance__run_instances_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_no_instances
    ec2.run_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.create_instance(
            ec2,
            fixtures.instance_name,
            fixtures.key_name,
            fixtures.security_group,
        )
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.run_instances.assert_called_once_with(
        ImageId="ami-08e4e35cccc6189f4",
        MaxCount=1,
        MinCount=1,
        InstanceType="c5a.xlarge",
        KeyName=fixtures.key_name,
        SecurityGroupIds=[fixtures.security_group],
        EnclaveOptions={"Enabled": True},
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
                    {"Key": "Name", "Value": fixtures.instance_name},
                ],
            },
        ],
    )


@patch("iac.instance.describe_instances")
def test_terminate_instance__happy_path(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = [
        fixtures.describe_instances_ret_one_instance,
        fixtures.describe_instances_ret_no_instances,
    ]

    ret = iac.terminate_instance(ec2, fixtures.instance_name)
    assert ret.name == fixtures.instance_name
    assert ret.id == fixtures.instance_id

    mock_describe_instances.assert_called_with(ec2, fixtures.instance_name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[fixtures.instance_id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__instance_not_running(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_no_instances

    with raises(iac.IACInstanceWarning) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value.error_code == iac.IACErrorCode.NO_SUCH_INSTANCE

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__describe_instances_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__name_collision(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_two_instances

    with raises(iac.IACInstanceError) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value.error_code == iac.IACErrorCode.INSTANCE_NAME_COLLISION

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__cloud_terminate_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_one_instance
    ec2.terminate_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_once_with(ec2, fixtures.instance_name)
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[fixtures.instance_id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__cloud_terminate_error(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = [
        fixtures.describe_instances_ret_one_instance,
        fixtures.describe_instances_ret_one_instance,
    ]

    with raises(iac.IACInstanceError) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value.error_code == iac.IACErrorCode.INSTANCE_TERMINATION_FAIL

    mock_describe_instances.assert_called_with(ec2, fixtures.instance_name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[fixtures.instance_id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__describe_instances_second_call_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = [
        fixtures.describe_instances_ret_one_instance,
        fixtures.exp_exc,
    ]

    with raises(Exception) as exc_info:
        iac.terminate_instance(ec2, fixtures.instance_name)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_with(ec2, fixtures.instance_name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[fixtures.instance_id])


@patch("iac.instance.describe_instances")
def test_list_instances__happy_path_no_instances(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_no_instances

    ret = iac.list_instances(ec2)
    assert ret == []

    mock_describe_instances.assert_called_with(ec2)


@patch("iac.instance.describe_instances")
def test_list_instances__happy_path_one_instance(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = fixtures.describe_instances_ret_one_instance

    ret = iac.list_instances(ec2)
    assert ret[0].name == fixtures.instance_name
    assert ret[0].id == fixtures.instance_id
    assert ret[0].key_name == fixtures.key_name
    assert ret[0].tags == [
        {"Key": "Deployment", "Value": "Sequencer"},
        {"Key": "Name", "Value": "test-instance"},
    ]

    mock_describe_instances.assert_called_with(ec2)


@patch("iac.instance.describe_instances")
def test_list_instances__describe_instances_exception(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.side_effect = fixtures.exp_exc

    with raises(Exception) as exc_info:
        iac.list_instances(ec2)
    assert exc_info.value is fixtures.exp_exc

    mock_describe_instances.assert_called_with(ec2)
