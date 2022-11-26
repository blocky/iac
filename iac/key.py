import os
from dataclasses import dataclass
from pprint import pformat
from typing import TypeVar

import botocore.client
import botocore.exceptions

import iac.aws
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACWarning, IACError, IACErrorCode


class IACKeyError(IACError):
    pass


class IACKeyWarning(IACWarning):
    pass


KeySelf = TypeVar("KeySelf", bound="Key")


@dataclass(frozen=True)
class Key:
    name: str
    tags: [iac.aws.Tag] = None

    @staticmethod
    def from_aws_key_pair(key_pair: dict) -> KeySelf:
        return Key(
            name=key_pair["KeyName"],
            tags=key_pair["Tags"],
        )

    @staticmethod
    def to_dict(key: KeySelf) -> dict:
        return key.__dict__


@dataclass(frozen=True)
class KeyFile:
    path: str
    username: str


@dataclass(frozen=True)
class KeyFileManager:
    folder: str
    # Note that the `create_instance` uses an image with id
    # "ami-08e4e35cccc6189f4".  The OS of of that image is amazon-linux.
    # In amazon-linux, the default user account is "ec2-user",
    # which is the reason for the default. If the OS of the image changes,
    # this simple default username initialization may need to change.
    username: str = "ec2-user"

    @staticmethod
    def open_as_600(path, flags):
        return os.open(path, flags, 0o600)

    def key_file(self, key_name: str) -> KeyFile:
        return KeyFile(
            path=os.path.join(self.folder, key_name + ".pem"),
            username=self.username,
        )

    def create(self, name: str, material: str) -> KeyFile:
        key_file = self.key_file(name)

        with open(
            key_file.path,
            mode="x",
            encoding="utf-8",
            opener=self.open_as_600
        ) as file:
            file.write(material)
        return key_file

    def delete(self, name: str) -> str:
        key_file = self.key_file(name)
        try:
            os.remove(key_file.path)
        except FileNotFoundError:
            pass
        return key_file


def describe_key_pairs(ec2: botocore.client.BaseClient, key_name: str = None) -> dict:
    filters = [
        {"Name": "tag:" + DEPLOYMENT_TAG, "Values": [SEQUENCER_TAG]},
    ]

    if key_name is None:
        return ec2.describe_key_pairs(Filters=filters)

    try:
        return ec2.describe_key_pairs(KeyNames=[key_name], Filters=filters)
    except botocore.exceptions.ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidKeyPair.NotFound":
            raise IACKeyWarning(IACErrorCode.NO_SUCH_KEY, pformat(exc.response)) from exc
        raise exc


def create_key_pair(
    ec2: botocore.client.BaseClient,
    kfm: KeyFileManager,
    key_name: str,
) -> Key:
    try:
        res = ec2.create_key_pair(
            KeyName=key_name,
            KeyType="rsa",
            KeyFormat="pem",
            TagSpecifications=[
                {
                    "ResourceType": "key-pair",
                    "Tags": [
                        {"Key": DEPLOYMENT_TAG, "Value": SEQUENCER_TAG},
                    ],
                },
            ],
        )
    except botocore.exceptions.ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidKeyPair.Duplicate":
            raise IACKeyWarning(IACErrorCode.DUPLICATE_KEY, pformat(exc.response)) from exc
        raise exc

    kfm.create(key_name, res["KeyMaterial"])

    return Key(name=res["KeyName"])


def delete_key_pair(
    ec2: botocore.client.BaseClient,
    kfm: KeyFileManager,
    key_name: str,
) -> Key:
    res = describe_key_pairs(ec2, key_name)

    if len(res["KeyPairs"]) != 1:
        raise IACKeyError(
            IACErrorCode.NO_SUCH_KEY,
            f"Found not exactly one key {key_name} to delete",
        )

    ec2.delete_key_pair(KeyName=key_name)

    try:
        res = describe_key_pairs(ec2, key_name)
        if len(res["KeyPairs"]) != 0:
            raise IACKeyError(
                IACErrorCode.KEY_DELETE_FAIL,
                f"Key '{key_name}' was not deleted",
            )
    except IACKeyWarning as exc:
        if exc.error_code != IACErrorCode.NO_SUCH_KEY:
            raise exc

    kfm.delete(key_name)

    return Key.from_aws_key_pair(res["KeyPairs"][0])


def list_key_pairs(ec2: botocore.client.BaseClient) -> [Key]:
    res = describe_key_pairs(ec2)
    return [Key.from_aws_key_pair(key_pair) for key_pair in res["KeyPairs"]]
