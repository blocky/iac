from dataclasses import dataclass
from typing import TypeVar

import botocore.client

import iac.aws
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACError, IACWarning, IACErrorCode


class IACInstanceError(IACError):
    pass


class IACInstanceWarning(IACWarning):
    pass


InstanceSelf = TypeVar("InstanceSelf", bound="Instance")


@dataclass(frozen=True)
class Instance:
    name: str
    id: str = None
    key_name: str = None
    tags: [iac.aws.Tag] = None
    public_dns_name: str = None

    @staticmethod
    def from_aws_instance(inst: dict) -> InstanceSelf:
        tags = inst["Tags"]
        name = next((t["Value"] for t in tags if t["Key"] == "Name"), None)
        return Instance(
            name=name,
            id=inst["InstanceId"],
            key_name=inst["KeyName"],
            tags=tags,
            public_dns_name=inst["PublicDnsName"],
        )


def describe_instances(
    ec2: botocore.client.BaseClient,
    instance_name: str = None,
) -> [Instance]:
    filters = [
        {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
        {"Name": "instance-state-name", "Values": ["pending", "running"]},
    ]
    if instance_name is not None:
        filters.append(
            {"Name": "tag:Name", "Values": [instance_name]},
        )

    res = ec2.describe_instances(Filters=filters)

    return list(
        Instance.from_aws_instance(inst) for r in res["Reservations"] for inst in r["Instances"]
    )


def _validate_running(instances: [Instance], instance_name: str):
    if len(instances) == 0:
        raise IACInstanceWarning(
            IACErrorCode.NO_SUCH_INSTANCE,
            f"Instance '{instance_name}' is not running",
        )


def _validate_not_multiple(instances: [Instance], instance_name: str):
    if len(instances) > 1:
        raise IACInstanceError(
            IACErrorCode.INSTANCE_NAME_COLLISION,
            f"More than one instance {instance_name} exists",
        )


def create_instance(
    ec2: botocore.client.BaseClient,
    instance_name: str,
    key_name: str,
    security_group: str,
) -> Instance:
    instances = describe_instances(ec2, instance_name)
    if len(instances) != 0:
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
    inst = res["Instances"][0]
    return Instance.from_aws_instance(inst)


def terminate_instance(ec2: botocore.client.BaseClient, instance_name: str) -> Instance:
    instances = describe_instances(ec2, instance_name)
    _validate_running(instances, instance_name)
    _validate_not_multiple(instances, instance_name)
    instance = instances[0]

    ec2.terminate_instances(InstanceIds=[instance.id])

    instances = describe_instances(ec2, instance.name)
    if len(instances) != 0:
        raise IACInstanceError(
            IACErrorCode.INSTANCE_TERMINATION_FAIL,
            f"Instance '{instance_name}' was not terminated",
        )

    return instance


def list_instances(ec2: botocore.client.BaseClient) -> [Instance]:
    return describe_instances(ec2)


def fetch_instance(ec2: botocore.client.BaseClient, instance_name: str) -> Instance:
    instances = describe_instances(ec2, instance_name)
    _validate_running(instances, instance_name)
    _validate_not_multiple(instances, instance_name)
    return instances[0]
