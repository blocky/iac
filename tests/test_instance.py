from unittest.mock import Mock, patch

from pytest import raises, mark

import iac


class ExpectedUncaughtInstanceException(Exception):
    pass


def test_instace_kind__from_str():
    assert iac.InstanceKind.from_str("standard") == iac.InstanceKind.STANDARD
    assert iac.InstanceKind.from_str("nitro") == iac.InstanceKind.NITRO
    with raises(iac.NEDInstanceError) as e:
        iac.InstanceKind.from_str("not-a-kind")
    assert e.value.error_code == iac.NEDErrorCode.INSTANCE_UNKNOWN_KIND
    assert "Cannot create instance kind from" in str(e.value)


@mark.parametrize("field", ["Tags", "InstanceId", "KeyName"])
def test_intance__from_aws_instance__error_in_structure(field, aws_parrot):
    resp = aws_parrot.describe_instances__one_instance
    inst = resp["Reservations"][0]["Instances"][0]
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
    assert not got
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def test_describe_instances__cloud_exception():
    want = ExpectedUncaughtInstanceException()
    ec2 = Mock()
    ec2.describe_instances.side_effect = want

    with raises(type(want)) as exc_info:
        iac.instance.describe_instances(ec2)
    assert exc_info.value is want
    assert_ec2_describe_instances_called_with_basic_filter(ec2)


def assert_nitro_ec2_run_instances_called_once(ec2, aws_parrot):
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


def assert_standard_ec2_run_instances_called_once(ec2, aws_parrot):
    ec2.run_instances.assert_called_once_with(
        ImageId="ami-08e4e35cccc6189f4",
        MaxCount=1,
        MinCount=1,
        InstanceType="t2.micro",
        KeyName=aws_parrot.key_name,
        SecurityGroupIds=[aws_parrot.security_group],
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
def test_create_instance__nitro_happy_path(mock_describe_instances, aws_parrot):
    ec2 = Mock()
    ec2.run_instances.return_value = aws_parrot.run_instances

    mock_describe_instances.return_value = []

    got = iac.create_instance(
        ec2,
        iac.InstanceKind.NITRO,
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
    assert_nitro_ec2_run_instances_called_once(ec2, aws_parrot)


@patch("iac.instance.describe_instances")
def test_create_instance__standard_happy_path(mock_describe_instances, aws_parrot):
    ec2 = Mock()
    ec2.run_instances.return_value = aws_parrot.run_instances

    mock_describe_instances.return_value = []

    got = iac.create_instance(
        ec2,
        iac.InstanceKind.STANDARD,
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
    assert_standard_ec2_run_instances_called_once(ec2, aws_parrot)


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
            iac.InstanceKind.NITRO,
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

    with raises(iac.NEDInstanceWarning) as exc_info:
        iac.create_instance(
            ec2,
            iac.InstanceKind.NITRO,
            aws_parrot.instance_name,
            aws_parrot.key_name,
            aws_parrot.security_group,
        )
    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_DUPLICATE

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
            iac.InstanceKind.NITRO,
            aws_parrot.instance_name,
            aws_parrot.key_name,
            aws_parrot.security_group,
        )
    assert exc_info.value is want

    mock_describe_instances.assert_called_once_with(ec2, aws_parrot.instance_name)
    assert_nitro_ec2_run_instances_called_once(ec2, aws_parrot)


@patch("iac.instance.describe_instances")
@mark.parametrize("state", ["shutting-down", "terminated"])
def test_terminate_instance__happy_path(
    mock_describe_instances,
    aws_parrot,
    state,
):
    ec2 = Mock()
    ec2.terminate_instances.return_value = aws_parrot.terminate_instances_result(state)

    want = iac.Instance(name="a", state="running", id="a_id")
    mock_describe_instances.return_value = [want]

    got = iac.terminate_instance(ec2, want.name)
    assert want == got

    mock_describe_instances.assert_called_once_with(ec2, want.name)
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[want.id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__instance_not_running(mock_describe_instances):
    ec2 = Mock()

    mock_describe_instances.return_value = []

    instance_name = "instance_name"
    with raises(iac.NEDInstanceWarning) as exc_info:
        iac.terminate_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_MISSING
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
    instance = iac.Instance(name=instance_name, state="running")
    mock_describe_instances.return_value = [instance] * 2

    with raises(iac.NEDInstanceError) as exc_info:
        iac.terminate_instance(ec2, instance_name)
    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_NAME_COLLISION

    mock_describe_instances.assert_called_once_with(ec2, instance_name)
    ec2.terminate_instances.assert_not_called()


@patch("iac.instance.describe_instances")
def test_terminate_instance__cloud_terminate_exception(mock_describe_instances):
    want = ExpectedUncaughtInstanceException()
    ec2 = Mock()
    ec2.terminate_instances.side_effect = want

    instance = iac.Instance(name="a", state="running", id="a_id")
    mock_describe_instances.return_value = [instance]

    with raises(type(want)) as exc_info:
        iac.terminate_instance(ec2, instance.name)
    assert exc_info.value is want

    mock_describe_instances.assert_called_once_with(ec2, instance.name)
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[instance.id])


@patch("iac.instance.describe_instances")
def test_terminate_instance__still_running(mock_describe_instances, aws_parrot):
    ec2 = Mock()
    ec2.terminate_instances.return_value = aws_parrot.terminate_instances_result("running")

    instance = iac.Instance(name="a", state="running", id="a_id")
    mock_describe_instances.return_value = [instance]

    with raises(iac.NEDInstanceError) as exc_info:
        iac.terminate_instance(ec2, instance.name)
    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_TERMINATION_FAIL

    mock_describe_instances.assert_called_once_with(ec2, instance.name)
    ec2.terminate_instances.assert_called_once_with(InstanceIds=[instance.id])


@patch("iac.instance.describe_instances")
def test_list_instances__happy_path(mock_describe_instances):
    ec2 = Mock()

    want = [iac.Instance("a", "running"), iac.Instance("b", "running")]
    mock_describe_instances.return_value = want

    got = iac.list_instances(ec2)
    assert want == got

    mock_describe_instances.assert_called_with(ec2)


@patch("iac.instance.describe_instances")
def test_fetch_instance__happy_path(mock_describe_instances):
    ec2 = Mock()

    want = iac.Instance(name="a", state="running")
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
    with raises(iac.NEDInstanceWarning) as exc_info:
        iac.fetch_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_MISSING
    mock_describe_instances.assert_called_once_with(ec2, instance_name)


@patch("iac.instance.describe_instances")
def test_fetch_instance__many_instances(mock_describe_instances):
    ec2 = Mock()

    instance_name = "instance_name"
    instance = iac.Instance(name=instance_name, state="running")
    mock_describe_instances.return_value = [instance] * 3

    with raises(iac.NEDInstanceError) as exc_info:
        iac.fetch_instance(ec2, instance_name)

    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_NAME_COLLISION
    mock_describe_instances.assert_called_once_with(ec2, instance_name)


def test_instance_running_barrier_wait_instance_ok_from_start():
    ec2 = Mock()

    running = iac.Instance(name="inst", state="running")
    got = iac.instance.InstanceRunningBarrier(ec2, 0, 2).wait(running)

    assert got == running
    ec2.assert_not_called()


@patch("iac.instance.fetch_instance")
def test_instance_running_barrier_wait_instance_ok_after_retry(
    mock_fetch_instance,
):
    ec2 = Mock()

    pending = iac.Instance(name="inst", state="pending")
    running = iac.Instance(name="inst", state="running")
    mock_fetch_instance.side_effect = [pending, running]

    got = iac.instance.InstanceRunningBarrier(ec2, 0, 2).wait(pending)

    assert got == running
    assert mock_fetch_instance.call_count == 2
    ec2.assert_not_called()


@patch("iac.instance.fetch_instance")
def test_instance_running_barrier_wait_instace_stuck_pending(
    mock_fetch_instance,
):
    ec2 = Mock()

    pending = iac.Instance(name="inst", state="pending")
    mock_fetch_instance.side_effect = [pending, pending]

    with raises(iac.NEDInstanceError) as exc_info:
        iac.instance.InstanceRunningBarrier(ec2, 0, 2).wait(pending)

    assert exc_info.value.error_code == iac.NEDErrorCode.INSTANCE_NOT_RUNNING
    assert mock_fetch_instance.call_count == 2
    ec2.assert_not_called()
