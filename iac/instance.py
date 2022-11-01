from dataclasses import dataclass
from typing import TypeVar
from enum import Enum

import botocore.client

import iac.aws
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACError, IACWarning, IACErrorCode


class IACInstanceError(IACError):
    pass


class IACInstanceWarning(IACWarning):
    pass


InstanceKindSelf = TypeVar("InstanceKindSelf", bound="InstanceKind")


class InstanceKind(Enum):
    STANDARD = "standard"
    NITRO = "nitro"

    @staticmethod
    def from_str(kind: str) -> InstanceKindSelf:
        match kind.lower():
            case "standard":
                return InstanceKind.STANDARD
            case "nitro":
                return InstanceKind.NITRO
            case _:
                raise IACInstanceError(
                    IACErrorCode.NO_SUCH_INSTANCE_KIND,
                    f"Cannot create instance kind from '{kind}'",
                )


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

    @staticmethod
    def to_dict(instance: InstanceSelf) -> dict:
        return instance.__dict__


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


def _ec2_config(
    kind: InstanceKind,
    instance_name: str,
    key_name: str,
    security_group: str,
) -> dict:
    definition = {
        "ImageId": "ami-08e4e35cccc6189f4",
        "MaxCount": 1,
        "MinCount": 1,
        "KeyName": key_name,
        "SecurityGroupIds": [security_group],
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": DEPLOYMENT_TAG, "Value": SEQUENCER_TAG},
                    {"Key": "Name", "Value": instance_name},
                ],
            },
        ],
    }

    instance_type_key = "InstanceType"
    match kind:
        case InstanceKind.STANDARD:
            definition[instance_type_key] = "t2.micro"
        case InstanceKind.NITRO:
            definition[instance_type_key] = "c5a.xlarge"
            definition["EnclaveOptions"] = {"Enabled": True}
        case _:
            raise IACInstanceError(
                IACErrorCode.NO_SUCH_INSTANCE_KIND,
                f"Unknown instance kind '{kind}'",
            )
    return definition


def create_instance(
    ec2: botocore.client.BaseClient,
    kind: InstanceKind,
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

    config = _ec2_config(kind, instance_name, key_name, security_group)
    res = ec2.run_instances(**config)
    inst = res["Instances"][0]
    return Instance.from_aws_instance(inst)


def terminate_instance(ec2: botocore.client.BaseClient, instance_name: str) -> Instance:
    instances = describe_instances(ec2, instance_name)
    _validate_running(instances, instance_name)
    _validate_not_multiple(instances, instance_name)
    instance = instances[0]

    res = ec2.terminate_instances(InstanceIds=[instance.id])
    current_state = res["TerminatingInstances"][0]["CurrentState"]["Name"]
    if current_state not in {"shutting-down", "terminated"}:
        raise IACInstanceError(
            IACErrorCode.INSTANCE_TERMINATION_FAIL,
            f"Instance '{instance_name}' was not terminated state is '{current_state}'",
        )

    return instance


def list_instances(ec2: botocore.client.BaseClient) -> [Instance]:
    return describe_instances(ec2)


def fetch_instance(ec2: botocore.client.BaseClient, instance_name: str) -> Instance:
    instances = describe_instances(ec2, instance_name)
    _validate_running(instances, instance_name)
    _validate_not_multiple(instances, instance_name)
    return instances[0]
