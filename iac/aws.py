import csv
from dataclasses import dataclass
from typing import TypedDict

import boto3

DEPLOYMENT_TAG = "Deployment"
SEQUENCER_TAG = "Sequencer"


class Tag(TypedDict):
    key: str
    value: str


@dataclass(frozen=True)
class Credentials:
    access_key: str
    secret_key: str


def get_credentials(cred_file: str) -> Credentials:
    with open(cred_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        row = next(reader)
    return Credentials(row["Access key ID"], row["Secret access key"])


class AWSClient:
    def __init__(self, creds: Credentials, region: str) -> None:
        self.ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds.access_key,
            aws_secret_access_key=creds.secret_key,
            region_name=region,
        )

        self.route53 = boto3.client(
            "route53",
            aws_access_key_id=creds.access_key,
            aws_secret_access_key=creds.secret_key,
        )
