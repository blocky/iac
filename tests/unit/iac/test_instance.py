from unittest.mock import Mock, patch

from pytest import raises, mark

from .context import iac


class ExpectedUncaughtInstanceException(Exception):
    pass


@mark.parametrize("field", ["Tags", "InstanceId", "KeyName", "PublicDnsName"])
def test_intance__from_aws_instance__error_in_structure(field, aws_parrot):
    inst = aws_parrot.describe_instances__one_instance["Reservations"][0]["Instances"][0]
    del inst[field]
    with raises(KeyError):
        iac.Instance.from_aws_instance(inst)


def test_intance__from_aws_instance__name_missing(aws_parrot):
    inst = aws_parrot.describe_instances__one_instance["Reservations"][0]["Instances"][0]

    tags = [{"Key": "X", "Value": "Y"}]
    inst["Tags"] = tags
    ret = iac.Instance.from_aws_instance(inst)

    assert ret.name is None
    assert ret.id == aws_parrot.instance_id
    assert ret.key_name == aws_parrot.key_name
    assert ret.tags == tags
    assert ret.public_dns_name is aws_parrot.instance_public_dns


def test_intance__from_aws_instance__happy_path(aws_parrot):
    inst = aws_parrot.describe_instances__one_instance["Reservations"][0]["Instances"][0]
    ret = iac.Instance.from_aws_instance(inst)

    assert ret.name == aws_parrot.instance_name
    assert ret.id == aws_parrot.instance_id
    assert ret.key_name == aws_parrot.key_name
    assert ret.tags == [
        {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
        {"Key": "Name", "Value": aws_parrot.instance_name},
    ]
    assert ret.public_dns_name is aws_parrot.instance_public_dns


def assert_ec2_describe_instances_called_with_basic_filter(ec2):
    filters = [
        {"Name": "tag:" + iac.DEPLOYMENT_TAG, "Values": [iac.SEQUENCER_TAG]},
        {"Name": "instance-state-name", "Values": ["pending", "running"]},
    ]
    ec2.describe_instances.assert_called_with(Filters=filters)


def assert_ec2_describe_instances_called_with_name_filter(ec2, name):
    filters = [
        {"Name": "tag:" + iac.DEPLOYMENT_TAG, "Values": [iac.SEQUENCER_TAG]},
        {"Name": "instance-state-name", "Values": ["pending", "running"]},
        {"Name": "tag:Name", "Values": [name]},
    ]
    ec2.describe_instances.assert_called_with(Filters=filters)


def test_describe_instances__happy_path_no_instance_name(aws_parrot):
    ec2 = Mock()
    ec2.describe_instances.return_value = aws_parrot.describe_instances__one_instance

    got = iac.instance.describe_instances(ec2)
    assert [aws_parrot.instance] == got
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def test_describe_instances__happy_path_instance_name(aws_parrot):
    ec2 = Mock()
    ec2.describe_instances.return_value = aws_parrot.describe_instances__one_instance

    got = iac.instance.describe_instances(ec2, aws_parrot.instance_name)
    assert [aws_parrot.instance] == got
    assert_ec2_describe_instances_called_with_name_filter(ec2, aws_parrot.instance_name)


def test_describe_instances__happy_path_many_instances(aws_parrot):
    ec2 = Mock()
    ec2.describe_instances.return_value = aws_parrot.describe_instances__many_instances

    got = iac.instance.describe_instances(ec2)
    assert [aws_parrot.other_instance, aws_parrot.instance] == got
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def test_describe_instances__happy_path_no_instances(aws_parrot):
    ec2 = Mock()
    ec2.describe_instances.return_value = aws_parrot.describe_instances__no_instances

    got = iac.instance.describe_instances(ec2)
    assert [] == got
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def test_describe_instances__cloud_exception():
    want = ExpectedUncaughtInstanceException()
    ec2 = Mock()
    ec2.describe_instances.side_effect = want

    with raises(type(want)) as exc_info:
        iac.instance.describe_instances(ec2)
    assert exc_info.value is want
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def assert_ec2_run_instances_called_once(ec2, aws_parrot):
    ec2.run_instances.assert_called_once_with(
        ImageId="ami-08e4e35cccc6189f4",
        MaxCount=1,
        MinCount=1,
        InstanceType="c5a.xlarge",
        KeyName=aws_parrot.key_name,
        SecurityGroupIds=[aws_parrot.security_group],
        EnclaveOptions={"Enabled": True},
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
                    {"Key": "Name", "Value": aws_parrot.instance_name},
                ],
            },
        ],
    )


@patch("iac.instance.describe_instances")
def test_create_instance__happy_path(mock_describe_instances, aws_parrot):
    ec2 = Mock()
    ec2.run_instances.return_value = aws_parrot.run_instances

    mock_describe_instances.return_value = []

    got = iac.create_instance(
        ec2,
        aws_parrot.instance_name,
        aws_parrot.key_name,
        aws_parrot.security_group,
    )
    assert got.name == aws_parrot.instance_name
    assert got.id == aws_parrot.instance_id
    assert got.key_name == aws_parrot.key_name
    assert got.public_dns_name == ""
    assert got.tags == [
        {"Key": iac.DEPLOYMENT_TAG, "Value": iac.SEQUENCER_TAG},
        {"Key": "Name", "Value": aws_parrot.instance_name},
    ]

    mock_describe_instances.assert_called_once_with(ec2, aws_parrot.instance_name)
    assert_ec2_run_instances_called_once(ec2, aws_parrot)


@patch("iac.instance.describe_instances")
def test_create_instance__describe_instances_error(
    mock_describe_instances,
    aws_parrot,
):
    ec2 = Mock()

    want = ExpectedUncaughtInstanceException()
    mock_describe_instances.side_effect = want

    with raises(type(want)) as exc_info:
        iac.create_instance(
            ec2,
            aws_parrot.instance_name,
            aws_parrot.key_name,
            aws_parrot.security_group,
        )
    assert exc_info.value is want

    mock_describe_instances.assert_called_once_with(ec2, aws_parrot.instance_name)
    ec2.run_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_create_instance__instance_already_exists(
    mock_describe_instances,
    aws_parrot,
):
    ec2 = Mock()

    mock_describe_instances.return_value = [aws_parrot.instance]

    with raises(iac.IACInstanceWarning) as exc_info:
        iac.create_instance(
            ec2,
            aws_parrot.instance_name,
            aws_parrot.key_name,
            aws_parrot.security_group,
        )
    assert exc_info.value.error_code == iac.IACErrorCode.DUPLICATE_INSTANCE

    mock_describe_instances.assert_called_once_with(ec2, aws_parrot.instance_name)
    ec2.run_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_create_instance__run_instances_exception(
    mock_describe_instances,
    aws_parrot,
):
    want = ExpectedUncaughtInstanceException()
    ec2 = Mock()
    ec2.run_instances.side_effect = want

    mock_describe_instances.return_value = []

    with raises(type(want)) as exc_info:
        iac.create_instance(
            ec2,
            aws_parrot.instance_name,
            aws_parrot.key_name,
            aws_parrot.security_group,
        )
    assert exc_info.value is want

    mock_describe_instances.assert_called_once_with(ec2, aws_parrot.instance_name)
    assert_ec2_run_instances_called_once(ec2, aws_parrot)


@patch("iac.instance.describe_instances")
def test_terminate_instance__happy_path(mock_describe_instances):
    ec2 = Mock()

    want = iac.Instance(name="a", id="a_id")
    mock_describe_instances.side_effect = [[want], []]

    got = iac.terminate_instance(ec2, want.name)
    assert want == got

    mock_describe_instances.assert_called_with(ec2, want.name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[want.id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__instance_not_running(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = []

    instance_name = "instance_name"
    with raises(iac.IACInstanceWarning) as exc_info:
        iac.terminate_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.IACErrorCode.NO_SUCH_INSTANCE
    mock_describe_instances.assert_called_once_with(ec2, instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__describe_instances_exception(mock_describe_instances):
    ec2 = Mock()

    instance_name = "name"
    want = ExpectedUncaughtInstanceException()
    mock_describe_instances.side_effect = want

    with raises(type(want)) as exc_info:
        iac.terminate_instance(ec2, instance_name)

    assert exc_info.value is want
    mock_describe_instances.assert_called_once_with(ec2, instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__name_collision(mock_describe_instances):
    ec2 = Mock()

    instance_name = "a"
    mock_describe_instances.return_value = [iac.Instance(instance_name)] * 2

    with raises(iac.IACInstanceError) as exc_info:
        iac.terminate_instance(ec2, instance_name)
    assert exc_info.value.error_code == iac.IACErrorCode.INSTANCE_NAME_COLLISION

    mock_describe_instances.assert_called_once_with(ec2, instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__cloud_terminate_exception(mock_describe_instances):
    want = ExpectedUncaughtInstanceException()
    ec2 = Mock()
    ec2.terminate_instances.side_effect = want

    instance = iac.Instance(name="a", id="a_id")
    mock_describe_instances.return_value = [instance]

    with raises(type(want)) as exc_info:
        iac.terminate_instance(ec2, instance.name)
    assert exc_info.value is want

    mock_describe_instances.assert_called_once_with(ec2, instance.name)
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[instance.id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__cloud_terminate_failed(mock_describe_instances):
    ec2 = Mock()

    instance = iac.Instance(name="a", id="a_id")
    mock_describe_instances.side_effect = [[instance]] * 2

    with raises(iac.IACInstanceError) as exc_info:
        iac.terminate_instance(ec2, instance.name)
    assert exc_info.value.error_code == iac.IACErrorCode.INSTANCE_TERMINATION_FAIL

    mock_describe_instances.assert_called_with(ec2, instance.name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[instance.id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__describe_instances_second_call_exception(mock_describe_instances):
    ec2 = Mock()

    want = ExpectedUncaughtInstanceException()
    instance = iac.Instance(name="a", id="a_id")
    mock_describe_instances.side_effect = [[instance], want]

    with raises(type(want)) as exc_info:
        iac.terminate_instance(ec2, instance.name)
    assert exc_info.value is want

    mock_describe_instances.assert_called_with(ec2, instance.name)
    assert mock_describe_instances.call_count == 2
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[instance.id])


@patch("iac.instance.describe_instances")
def test_list_instances__happy_path(mock_describe_instances):
    ec2 = Mock()

    want = [iac.Instance("a"), iac.Instance("b")]
    mock_describe_instances.return_value = want

    got = iac.list_instances(ec2)
    assert want == got

    mock_describe_instances.assert_called_with(ec2)


@patch("iac.instance.describe_instances")
def test_fetch_instance__happy_path(mock_describe_instances):
    ec2 = Mock()

    want = iac.Instance("a")
    mock_describe_instances.return_value = [want]

    got = iac.fetch_instance(ec2, want.name)
    assert want == got

    mock_describe_instances.assert_called_with(ec2, want.name)
    assert mock_describe_instances.call_count == 1


@patch("iac.instance.describe_instances")
def test_fetch_instance__no_instance(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = []

    instance_name = "instance_name"
    with raises(iac.IACInstanceWarning) as exc_info:
        iac.fetch_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.IACErrorCode.NO_SUCH_INSTANCE
    mock_describe_instances.assert_called_once_with(ec2, instance_name)


@patch("iac.instance.describe_instances")
def test_fetch_instance__many_instances(mock_describe_instances):
    ec2 = Mock()

    instance_name = "instance_name"
    mock_describe_instances.return_value = [iac.Instance(instance_name)] * 3

    with raises(iac.IACInstanceError) as exc_info:
        iac.fetch_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.IACErrorCode.INSTANCE_NAME_COLLISION
    mock_describe_instances.assert_called_once_with(ec2, instance_name)
