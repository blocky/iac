import pytest
from pytest import raises

import iac
from ned.aws import Credentials


def test_get_credentials__happy_path(credential_file_name):
    creds = ned.aws.get_credentials(credential_file_name)
    assert creds.access_key == "test-access-key"
    assert creds.secret_key == "test-secret-key"


def test_get_credentials__bad_file_name():
    with raises(FileNotFoundError):
        ned.aws.get_credentials("bad_file_name")


@pytest.mark.parametrize(
    "creds, region",
    [
        [Credentials("a", "b"), "c"],
        [Credentials("a", ""), "c"],
        [Credentials("", "b"), "c"],
        [Credentials("", ""), "c"],
    ],
)
def test_make_ec2_client__happy_path(creds: Credentials, region: str):
    client = ned.AWSClient(creds, region)
    assert client.ec2 is not None
    assert client.route53 is not None


def test_make_ec2_client__empty_region():
    with raises(ValueError):
        ned.AWSClient(Credentials("a", "b"), "")
