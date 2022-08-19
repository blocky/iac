import json
import os
from os.path import abspath, join

import click

import iac


DEFAULT_CONFIG_FILE = abspath(join(os.getcwd(), "setup", "config.toml"))

IAC_CMD_KWARGS = {
    "obj": {},
    "auto_envvar_prefix": "BKY_IAC",
}


def console(to_dict, data):
    try:
        as_dict = [to_dict(d) for d in data]
    except TypeError:
        as_dict = to_dict(data)
    click.echo(json.dumps(as_dict, indent=2))


def fail_on_nodebug(ctx):
    if not ctx.obj["conf"].debug:
        raise click.UsageError("Cannot run command in nodebug mode")


def fail_on_debug(ctx):
    if ctx.obj["conf"].debug:
        raise click.UsageError("Cannot run command in debug mode")


@click.group()
@click.option("--config-file", default=DEFAULT_CONFIG_FILE, show_envvar=True, show_default=True)
@click.option("--access-key", show_envvar=True)
@click.option("--secret-key", show_envvar=True)
@click.option("--region", show_envvar=True)
@click.option("--debug/--no-debug", default=False, show_envvar=True, show_default=True)
@click.pass_context
# pylint: disable = too-many-arguments
def iac_cmd(ctx, config_file, access_key, secret_key, region, debug):  # noqa: R0913
    conf = iac.Config.from_toml(config_file)

    conf.debug = debug or conf.debug
    conf.region = region or conf.region
    conf.access_key = access_key or conf.access_key
    conf.secret_key = secret_key or conf.secret_key
    creds = (
        iac.aws.Credentials(conf.access_key, conf.secret_key)
        if conf.access_key and conf.secret_key
        else iac.get_credentials(conf.cred_file)
    )

    ctx.obj["ec2"] = iac.make_ec2_client(creds, conf.region)
    ctx.obj["conf"] = conf


@click.group(name="key")
@click.option("--key-name", show_envvar=True)
@click.option("--secrets-folder", show_envvar=True)
@click.pass_context
def key_cmd(ctx, key_name, secrets_folder):
    conf = ctx.obj["conf"]

    conf.key_name = key_name or conf.key_name
    conf.secrets_folder = secrets_folder or conf.secrets_folder

    ctx.obj["conf"] = conf


@click.command(name="create")
@click.pass_context
def key_create_cmd(ctx):
    fail_on_debug(ctx)

    conf = ctx.obj["conf"]
    ec2 = ctx.obj["ec2"]

    kfm = iac.KeyFileManager(conf.secrets_folder)
    key = iac.create_key_pair(ec2, kfm, conf.key_name)
    console(iac.Key.to_dict, key)


@click.command(name="delete")
@click.pass_context
def key_delete_cmd(ctx):
    fail_on_debug(ctx)

    conf = ctx.obj["conf"]
    ec2 = ctx.obj["ec2"]

    kfm = iac.KeyFileManager(conf.secrets_folder)
    key = iac.delete_key_pair(ec2, kfm, conf.key_name)
    console(iac.Key.to_dict, key)


@click.command(name="list")
@click.pass_context
def key_list_cmd(ctx):
    fail_on_debug(ctx)

    keys = iac.list_key_pairs(ctx.obj["ec2"])
    console(iac.Key.to_dict, keys)


@click.command(name="dbgconf")
@click.pass_context
def x_dbgconf_cmd(ctx):
    fail_on_nodebug(ctx)

    console(iac.Config.to_dict, ctx.obj["conf"])


iac_cmd.add_command(key_cmd)
key_cmd.add_command(key_create_cmd)
key_cmd.add_command(key_delete_cmd)
key_cmd.add_command(key_list_cmd)
key_cmd.add_command(x_dbgconf_cmd)


@click.group(name="instance")
@click.option("--instance-name", show_envvar=True)
@click.option("--key-name", show_envvar=True)
@click.option("--security-group", show_envvar=True)
@click.pass_context
def instance_cmd(ctx, instance_name, key_name, security_group):
    conf = ctx.obj["conf"]

    conf.instance_name = instance_name or conf.instance_name
    conf.key_name = key_name or conf.key_name
    conf.security_group = security_group or conf.security_group

    ctx.obj["conf"] = conf


@click.command(name="create")
@click.pass_context
def instance_create_cmd(ctx):
    fail_on_debug(ctx)

    conf = ctx.obj["conf"]
    instance = iac.create_instance(
        ctx.obj["ec2"],
        conf.instance_name,
        conf.key_name,
        conf.security_group,
    )
    console(iac.Instance.to_dict, instance)


@click.command(name="terminate")
@click.pass_context
def instance_terminate_cmd(ctx):
    fail_on_debug(ctx)

    instance = iac.terminate_instance(ctx.obj["ec2"], ctx.obj["conf"].instance_name)
    console(iac.Instance.to_dict, instance)


@click.command(name="list")
@click.pass_context
def instance_list_cmd(ctx):
    fail_on_debug(ctx)

    instances = iac.list_instances(ctx.obj["ec2"])
    console(iac.Instance.to_dict, instances)


iac_cmd.add_command(instance_cmd)
instance_cmd.add_command(instance_create_cmd)
instance_cmd.add_command(instance_terminate_cmd)
instance_cmd.add_command(instance_list_cmd)
instance_cmd.add_command(x_dbgconf_cmd)
