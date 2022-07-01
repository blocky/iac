from dataclasses import dataclass

import botocore.client

import iac.aws
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACError, IACWarning, IACErrorCode


class IACInstanceError(IACError):
    pass


class IACInstanceWarning(IACWarning):
    pass


@dataclass(frozen=True)
class Instance:
    name: str
    id: str = None
    key_name: str = None
    tags: [iac.aws.Tag] = None


def describe_instances(ec2: botocore.client.BaseClient, instance_name: str = None) -> dict:
    filters = [
        {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        {"Name": "instance-state-name", "Values": ["pending", "running"]},
    ]
    if instance_name is not None:
        filters.append(
            {"Name": "tag:Name", "Values": [instance_name]},
        )
    return ec2.describe_instances(Filters=filters)


def create_instance(
    ec2: botocore.client.BaseClient,
    instance_name: str,
    key_name: str,
    security_group: str,
) -> Instance:
    res = describe_instances(ec2, instance_name)
    if len(res["Reservations"]) and len(res["Reservations"][0]["Instances"]) > 0:
        raise IACInstanceWarning(
            IACErrorCode.DUPLICATE_INSTANCE,
            f"Instance '{instance_name}' already exists",
        )

    res = ec2.run_instances(
        ImageId="ami-08e4e35cccc6189f4",
        MaxCount=1,
        MinCount=1,
        InstanceType="c5a.xlarge",
        KeyName=key_name,
        SecurityGroupIds=[security_group],
        EnclaveOptions={"Enabled": True},
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": DEPLOYMENT_TAG, "Value": SEQUENCER_TAG},
                    {"Key": "Name", "Value": instance_name},
                ],
            },
        ],
    )
    name = None
    for tag in res["Instances"][0]["Tags"]:
        if tag["Key"] == "Name":
            name = tag["Value"]

    return Instance(
        name=name,
        id=res["Instances"][0]["InstanceId"],
        key_name=res["Instances"][0]["KeyName"],
        tags=res["Instances"][0]["Tags"],
    )


def terminate_instance(ec2: botocore.client.BaseClient, instance_name: str) -> Instance:
    res = describe_instances(ec2, instance_name)
    if len(res["Reservations"]) == 0:
        raise IACInstanceWarning(
            IACErrorCode.NO_SUCH_INSTANCE,
            f"Instance '{instance_name}' is not running",
        )
    if len(res["Reservations"][0]["Instances"]) > 1:
        raise IACInstanceError(
            IACErrorCode.INSTANCE_NAME_COLLISION,
            f"More than one instance {instance_name} exists",
        )

    instance_id = res["Reservations"][0]["Instances"][0]["InstanceId"]
    ec2.terminate_instances(InstanceIds=[instance_id])

    res = describe_instances(ec2, instance_name)
    if len(res["Reservations"]) != 0:
        raise IACInstanceError(
            IACErrorCode.INSTANCE_TERMINATION_FAIL,
            f"Instance '{instance_name}' was not terminated",
        )

    return Instance(name=instance_name, id=instance_id)


def list_instances(ec2: botocore.client.BaseClient) -> [Instance]:
    res = describe_instances(ec2)

    if len(res["Reservations"]) == 0:
        return []
    inst_list = []
    for inst in res["Reservations"][0]["Instances"]:
        name = None
        for tag in inst["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        inst_list.append(
            Instance(
                name=name,
                id=inst["InstanceId"],
                key_name=inst["KeyName"],
                tags=inst["Tags"],
            )
        )
    return inst_list
