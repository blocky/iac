import os
from dataclasses import dataclass
from pprint import pformat

import botocore.client
import botocore.exceptions

import iac.aws
import utils.utils as utl
from iac.aws import DEPLOYMENT_TAG, SEQUENCER_TAG
from iac.exception import IACWarning, IACError, IACErrorCode


class IACKeyError(IACError):
    pass


class IACKeyWarning(IACWarning):
    pass


@dataclass(frozen=True)
class Key:
    name: str
    tags: [iac.aws.Tag] = None


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


def key_file_name(key_name: str) -> str:
    return os.path.join(utl.secrets_path(), key_name + ".pem")


def create_key_pair_file(key_name: str, key_material: str) -> str:
    key_fn = key_file_name(key_name)
    if os.path.exists(key_fn):
        raise IACKeyError(IACErrorCode.KEY_FILE_EXISTS, f"Key file {key_fn} already exists")
    with open(key_fn, mode="w", encoding="utf-8") as file:
        file.write(key_material)
    return key_fn


def delete_key_pair_file(key_name: str) -> str:
    key_fn = key_file_name(key_name)
    try:
        os.remove(key_fn)
    except FileNotFoundError as exc:
        raise IACKeyError(
            IACErrorCode.NO_SUCH_KEY_FILE, f"Key file {key_fn} does not exist"
        ) from exc
    return key_fn


def create_key_pair(ec2: botocore.client.BaseClient, key_name: str) -> Key:
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

    create_key_pair_file(key_name, res["KeyMaterial"])

    return Key(name=res["KeyName"])


def delete_key_pair(ec2: botocore.client.BaseClient, key_name: str) -> Key:
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

    delete_key_pair_file(key_name)

    return Key(name=res["KeyPairs"][0]["KeyName"], tags=res["KeyPairs"][0]["Tags"])


def list_key_pairs(ec2: botocore.client.BaseClient) -> [Key]:
    res = describe_key_pairs(ec2)

    if len(res["KeyPairs"]) == 0:
        return []

    key_list = []
    for key in res["KeyPairs"]:
        key_list.append(
            Key(
                name=key["KeyName"],
                tags=key["Tags"],
            )
        )
    return key_list
