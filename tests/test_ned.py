import json
from unittest.mock import patch, Mock, ANY

from pytest import mark
from click.testing import CliRunner

import iac
from ned import ned as app


def run_app(*args, **kwargs):
    # note that when setting up the click cli runner the arguments
    # in the invocation of the click command
    # needs to be the same as in the invocation call.
    #
    # For example, if __main__.py invokes the ned command as
    #
    #   def main():
    #       ned.iac_cmd(obj={}, auto_envvar_prefix="BKY_NED")
    #
    # We need to make sure that the `obj` and `auto_envvar_prefix` values are
    # the same in the CliRunner invocation:
    #
    #   CliRunner().invoke(app.iac_cmd, ..., obj={}, auto_envvar_prefix="BKY_NED")
    #
    # To make our lives easier, we can use the NED_CMD_KWARGS in both places.
    # So for example:
    #
    #   def main():
    #       ned.iac_cmd(**ned.NED_CMD_KWARGS)
    #
    # and
    #
    #    CliRunner().invoke(app.iac_cmd, ..., **app.NED_CMD_KWARGS)
    return CliRunner().invoke(
        app.iac_cmd, args, catch_exceptions=False, env=kwargs, **app.NED_CMD_KWARGS
    )


@patch("ned.get_credentials")
@patch("ned.AWSClient")
@mark.parametrize("subcommand", ["instance", "key", "config", "deploy"])
def test_setup_no_keys_or_creds(
    mock_aws_client_init,
    mock_get_credentials,
    subcommand,
    config_file_with_no_creds_name,
):
    result = run_app(
        f"--config-file={config_file_with_no_creds_name}",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_not_called()
    mock_aws_client_init.assert_not_called()


@patch("ned.get_credentials")
@patch("ned.AWSClient")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_setup_aws_client_uses_creds_file_when_missing_both_keys(
    mock_aws_client_init,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    client = Mock()
    mock_aws_client_init.return_value = client

    result = run_app(
        f"--config-file={config_file_name}",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_aws_client_init.assert_called_once_with(creds, ANY)


@patch("ned.get_credentials")
@patch("ned.AWSClient")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_setup_aws_client_uses_creds_file_when_missing_secret_key(
    mock_aws_client_init,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    client = Mock()
    mock_aws_client_init.return_value = client

    result = run_app(
        f"--config-file={config_file_name}",
        "--access-key=abc",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_aws_client_init.assert_called_once_with(creds, ANY)


@patch("ned.get_credentials")
@patch("ned.AWSClient")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_setup_aws_client_uses_creds_file_when_missing_access_key(
    mock_aws_client_init,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    creds = Mock()
    mock_get_credentials.return_value = creds

    client = Mock()
    mock_aws_client_init.return_value = client

    result = run_app(
        f"--config-file={config_file_name}",
        "--secret-key=123",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_called_once_with("my-cred-file.csv")
    mock_aws_client_init.assert_called_once_with(creds, ANY)


@patch("ned.get_credentials")
@patch("ned.AWSClient")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_setup_aws_client_uses_keys_when_both_keys_present(
    mock_aws_client_init,
    mock_get_credentials,
    subcommand,
    config_file_name,
):
    access_key = "abc"
    secret_key = "123"

    creds = ned.aws.Credentials(access_key, secret_key)

    client = Mock()
    mock_aws_client_init.return_value = client

    result = run_app(
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        subcommand,
        "--help",
    )
    assert result.exit_code == 0

    mock_get_credentials.assert_not_called()
    mock_aws_client_init.assert_called_once_with(creds, ANY)


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_dbgconf__error_when_not_in_debug(_m1, _m2, subcommand, config_file_name):
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


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_dbgconf__error_by_default(_m1, _m2, subcommand, config_file_name):
    result = run_app(
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 2
    assert result.output.endswith("Error: Cannot run command in nodebug mode\n")


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_dbgconf__ok_when_in_debug(_m1, _m2, subcommand, config_file_name):
    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        subcommand,
        "dbgconf",
    )
    assert result.exit_code == 0


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
@mark.parametrize(
    "subcmd,subsubcmd,args",
    [
        ("instance", "create", None),
        ("instance", "list", None),
        ("instance", "terminate", None),
        ("key", "create", None),
        ("key", "delete", None),
        ("key", "list", None),
        ("deploy", "copy", "xyz.txt"),
        ("deploy", "run", "ls"),
    ],
)
def test_normal_commands__fail_in_debug(
    _m1,
    _m2,
    subcmd,
    subsubcmd,
    args,
    config_file_name,
):

    cmd = [subcmd, subsubcmd]
    if args:
        cmd.append(args)

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=abc",
        "--secret-key=123",
        *cmd,
    )
    assert result.exit_code != 0
    assert result.output.endswith("Error: Cannot run command in debug mode\n")


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
@patch("ned.get_credentials")
@mark.parametrize("subcommand", ["instance", "key", "deploy"])
def test_dbgconf__sets_from_config(
    mock_get_credentials,
    _m1,
    _m2,
    subcommand,
    config_file_name,
):
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
    assert conf["instance_kind"] == "nitro"
    assert conf["fqdn"] == "my-fqdn"

    mock_get_credentials.assert_called_once_with(cred_file_name)


def test_dbgconf__instance_sets_from_command_line(config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    instance_name = "bob"
    key_name = "fred"
    security_group = "yum"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        f"--cred-file={cred_file_name}",
        f"--region={region}",
        "instance",
        f"--instance-name={instance_name}",
        f"--key-name={key_name}",
        f"--security-group={security_group}",
        "--no-nitro",
        "dbgconf",
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == "my-secrets-folder"
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == security_group
    assert conf["instance_kind"] == "standard"


def test_dbgconf__instance_sets_from_environment(config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    instance_name = "bob"
    key_name = "fred"
    security_group = "yum"
    instance_kind = "nitro"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "instance",
        "dbgconf",
        BKY_NED_ACCESS_KEY=access_key,
        BKY_NED_SECRET_KEY=secret_key,
        BKY_NED_CRED_FILE=cred_file_name,
        BKY_NED_REGION=region,
        BKY_NED_INSTANCE_INSTANCE_NAME=instance_name,
        BKY_NED_INSTANCE_KEY_NAME=key_name,
        BKY_NED_INSTANCE_SECURITY_GROUP=security_group,
        BKY_NED_INSTANCE_INSTANCE_KIND=instance_kind,
    )

    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == "my-secrets-folder"
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == security_group
    assert conf["instance_kind"] == instance_kind


def test_dbgconf__key_sets_from_command_line(config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        f"--cred-file={cred_file_name}",
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
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == "my-instance"
    assert conf["security_group"] == "my-security-group"


def test_dbgconf__key_sets_from_environment(config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "key",
        "dbgconf",
        BKY_NED_ACCESS_KEY=access_key,
        BKY_NED_SECRET_KEY=secret_key,
        BKY_NED_CRED_FILE=cred_file_name,
        BKY_NED_REGION=region,
        BKY_NED_KEY_KEY_NAME=key_name,
        BKY_NED_KEY_SECRETS_FOLDER=secrets_folder,
    )

    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == "my-instance"
    assert conf["security_group"] == "my-security-group"


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
def test_dbgconf__deploy_sets_from_command_line(_m1, _m2, config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"
    instance_name = "bob"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        f"--access-key={access_key}",
        f"--secret-key={secret_key}",
        f"--cred-file={cred_file_name}",
        f"--region={region}",
        "deploy",
        f"--instance-name={instance_name}",
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
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == "my-security-group"


@patch("ned.fetch_instance")
@patch("ned.RemoteCMDRunner.from_instance_and_key_file")
def test_dbgconf__deploy_sets_from_environment(_m1, _m2, config_file_name):
    access_key = "abc"
    secret_key = "123"
    cred_file_name = "abc123"
    region = "mars"
    key_name = "fred"
    secrets_folder = "secrets-folder"
    instance_name = "bob"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "deploy",
        "dbgconf",
        BKY_NED_ACCESS_KEY=access_key,
        BKY_NED_SECRET_KEY=secret_key,
        BKY_NED_CRED_FILE=cred_file_name,
        BKY_NED_REGION=region,
        BKY_NED_DEPLOY_INSTANCE_NAME=instance_name,
        BKY_NED_DEPLOY_KEY_NAME=key_name,
        BKY_NED_DEPLOY_SECRETS_FOLDER=secrets_folder,
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["region"] == region
    assert conf["access_key"] == access_key
    assert conf["secret_key"] == secret_key
    assert conf["cred_file"] == cred_file_name
    assert conf["key_name"] == key_name
    assert conf["secrets_folder"] == secrets_folder
    assert conf["instance_name"] == instance_name
    assert conf["security_group"] == "my-security-group"


def test_dbgconf__dns_sets_from_command_line(config_file_name):
    instance_name = "bob"
    fqdn = "flukeman"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=access",
        "--secret-key=secret",
        "dns",
        f"--instance-name={instance_name}",
        f"--fqdn={fqdn}",
        "dbgconf",
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["instance_name"] == instance_name
    assert conf["fqdn"] == fqdn


def test_dbgconf__dns_sets_from_environment(config_file_name):
    instance_name = "bob"
    fqdn = "flukeman"

    result = run_app(
        "--debug",
        f"--config-file={config_file_name}",
        "--access-key=access",
        "--secret-key=secret",
        "dns",
        "dbgconf",
        BKY_NED_DNS_INSTANCE_NAME=instance_name,
        BKY_NED_DNS_FQDN=fqdn,
    )
    assert result.exit_code == 0

    conf = json.loads(result.stdout)
    assert conf["debug"]
    assert conf["instance_name"] == instance_name
    assert conf["fqdn"] == fqdn
