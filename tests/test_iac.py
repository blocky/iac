import json
from unittest.mock import patch, Mock, ANY

from pytest import mark
from click.testing import CliRunner

import iac
from iac import iac as app


def run_app(*args, **kwargs):
    # note that when setting up the click cli runner the arguments
    # in the invocation of the click command
    # needs to be the same as in the invocation call.
    #
    # For example, if __main__.py invokes the iac command as
    #
    #   def main():
    #       iac.iac_cmd(obj={}, auto_envvar_prefix="BKY_IAC")
    #
    # We need to make sure that the `obj` and `auto_envvar_prefix` values are
    # the same in the CliRunner invocation:
    #
    #   CliRunner().invoke(app.iac_cmd, ..., obj={}, auto_envvar_prefix="BKY_IAC")
    #
    # To make our lives easier, we can use the IAC_CMD_KWARGS in both places.
    # So for example:
    #
    #   def main():
    #       iac.iac_cmd(**iac.IAC_CMD_KWARGS)
    #
    # and
    #
    #    CliRunner().invoke(app.iac_cmd, ..., **app.IAC_CMD_KWARGS)
    return CliRunner().invoke(
        app.iac_cmd, args, catch_exceptions=False, env=kwargs, **app.IAC_CMD_KWARGS
    )


@patch("iac.get_credentials")
@patch("iac.make_ec2_client")
@mark.parametrize("subcommand", ["instance", "key"])
def test_setup_make_ec2_client_uses_creds_file_when_missing_both_keys(
    mock_make_ec2_client,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    ec2 = Mock()
    mock_make_ec2_client.return_value = ec2

    result = run_app(
        f"--config-file={config_file_name}",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_make_ec2_client.assert_called_once_with(creds, ANY)


@patch("iac.get_credentials")
@patch("iac.make_ec2_client")
@mark.parametrize("subcommand", ["instance", "key"])
def test_setup_make_ec2_client_uses_creds_file_when_missing_secret_key(
    mock_make_ec2_client,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    ec2 = Mock()
    mock_make_ec2_client.return_value = ec2

    result = run_app(
        f"--config-file={config_file_name}",
        "--access-key=abc",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_make_ec2_client.assert_called_once_with(creds, ANY)


@patch("iac.get_credentials")
@patch("iac.make_ec2_client")
@mark.parametrize("subcommand", ["instance", "key"])
def test_setup_make_ec2_client_uses_creds_file_when_missing_access_key(
    mock_make_ec2_client,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    ec2 = Mock()
    mock_make_ec2_client.return_value = ec2

    result = run_app(
        f"--config-file={config_file_name}",
        "--secret-key=123",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_make_ec2_client.assert_called_once_with(creds, ANY)


@patch("iac.get_credentials")
@patch("iac.make_ec2_client")
@mark.parametrize("subcommand", ["instance", "key"])
def test_setup_make_ec2_client_uses_keys_when_both_keys_present(
    mock_make_ec2_client,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    access_key = "abc"
    secret_key = "123"

    creds = iac.aws.Credentials(access_key, secret_key)

    ec2 = Mock()
    mock_make_ec2_client.return_value = ec2

    result = run_app(
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_not_called()
    mock_make_ec2_client.assert_called_once_with(creds, ANY)


@mark.parametrize("subcommand", ["instance", "key"])
def test_dbgconf__error_when_not_in_debug(subcommand, config_file_name):
    result = run_app(
        "--no-debug",
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 2
    assert result.output.endswith("Error: Cannot run command in nodebug mode\n")


@mark.parametrize("subcommand", ["instance", "key"])
def test_dbgconf__error_by_default(subcommand, config_file_name):
    result = run_app(
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 2
    assert result.output.endswith("Error: Cannot run command in nodebug mode\n")


@mark.parametrize("subcommand", ["instance", "key"])
def test_dbgconf__ok_when_in_debug(subcommand, config_file_name):
    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 0


@mark.parametrize(
    "subcmd,subsubcmd",
    [
        ("instance", "create"),
        ("instance", "list"),
        ("instance", "terminate"),
        ("key", "create"),
        ("key", "delete"),
        ("key", "list"),
    ],
)
def test_normal_commands__fail_in_debug(subcmd, subsubcmd, config_file_name):
    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcmd,
        subsubcmd,
    )
    assert result.exit_code != 0
    assert result.output.endswith("Error: Cannot run command in debug mode\n")


@patch("iac.get_credentials")
@mark.parametrize("subcommand", ["instance", "key"])
def test_dbgconf__sets_from_config(mock_get_credentials, subcommand, config_file_name):
    creds = Mock()
    mock_get_credentials.return_value = creds
    cred_file_name = "my-cred-file.csv"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == "my-region"
    assert conf["access_key"] is None
    assert conf["secret_key"] is None
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == "my-key"
    assert conf["secrets_folder"] == "my-secrets-folder"
    assert conf["instance_name"] == "my-instance"
    assert conf["security_group"] == "my-security-group"

    mock_get_credentials.assert_called_once_with(cred_file_name)


def test_dbgconf__instance_sets_from_command_line(config_file_name):
    access_key = "abc"
    secret_key = "123"
    region = "mars"
    instance_name = "bob"
    key_name = "fred"
    security_group = "yum"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        f"--region={region}",
        "instance",
        f"--instance-name={instance_name}",
        f"--key-name={key_name}",
        f"--security-group={security_group}",
        "dbgconf",
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == "my-cred-file.csv"
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == "my-secrets-folder"
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == security_group


def test_dbgconf__instance_sets_from_environment(config_file_name):
    access_key = "abc"
    secret_key = "123"
    region = "mars"
    instance_name = "bob"
    key_name = "fred"
    security_group = "yum"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "instance",
        "dbgconf",
        BKY_IAC_ACCESS_KEY=access_key,
        BKY_IAC_SECRET_KEY=secret_key,
        BKY_IAC_REGION=region,
        BKY_IAC_INSTANCE_INSTANCE_NAME=instance_name,
        BKY_IAC_INSTANCE_KEY_NAME=key_name,
        BKY_IAC_INSTANCE_SECURITY_GROUP=security_group,
    )

    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == "my-cred-file.csv"
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == "my-secrets-folder"
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == security_group


def test_dbgconf__key_sets_from_command_line(config_file_name):
    access_key = "abc"
    secret_key = "123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        f"--region={region}",
        "key",
        f"--key-name={key_name}",
        f"--secrets-folder={secrets_folder}",
        "dbgconf",
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == "my-cred-file.csv"
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == "my-instance"
    assert conf["security_group"] == "my-security-group"


def test_dbgconf__key_sets_from_environment(config_file_name):
    access_key = "abc"
    secret_key = "123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "key",
        "dbgconf",
        BKY_IAC_ACCESS_KEY=access_key,
        BKY_IAC_SECRET_KEY=secret_key,
        BKY_IAC_REGION=region,
        BKY_IAC_KEY_KEY_NAME=key_name,
        BKY_IAC_KEY_SECRETS_FOLDER=secrets_folder,
    )

    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == "my-cred-file.csv"
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == "my-instance"
    assert conf["security_group"] == "my-security-group"
