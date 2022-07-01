from os.path import join

import pytest
from pytest import raises

from iac.aws import Credentials
from tests.unit.iac.context import iac
from utils.utils import secrets_path


def test_get_credentials__happy_path():
    file_name = join(secrets_path(), "credentials_for_testing.csv")
    creds = iac.aws.get_credentials(file_name)
    assert creds.access_key == "test-access-key"
    assert creds.secret_key == "test-secret-key"


def test_get_credentials__bad_file_name():
    with raises(FileNotFoundError):
        iac.aws.get_credentials("bad_file_name")


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
    ec2 = iac.aws.make_ec2_client(creds, region)
    assert ec2 is not None


def test_make_ec2_client__empty_region():
    with raises(ValueError):
        iac.aws.make_ec2_client(Credentials("a", "b"), "")
