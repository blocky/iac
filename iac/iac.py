import json
from os.path import join
from importlib import resources
from pathlib import Path

import click

import iac


APP_DATA_PATH = resources.path("iac", "data")
USER_DATA_PATH = join(Path.home(), ".config", "bky", "iac")
IAC_CMD_KWARGS = {
    "obj": {},
    "auto_envvar_prefix": "BKY_IAC",
}


def sample_config_file_name():
    return join(APP_DATA_PATH, "sample_config.toml")


def user_config_file_name():
    return join(USER_DATA_PATH, "config.toml")


def console(data, to_dict=None):
    out = data
    if to_dict:
        try:
            as_dict = [to_dict(d) for d in data]
        except TypeError:
            as_dict = to_dict(data)
        out = json.dumps(as_dict, indent=2)

    click.echo(out)


def fail_on_nodebug(ctx):
    if not ctx.obj["conf"].debug:
        raise click.UsageError("Cannot run command in nodebug mode")


def fail_on_debug(ctx):
    if ctx.obj["conf"].debug:
        raise click.UsageError("Cannot run command in debug mode")


@click.group()
@click.option("--config-file", show_envvar=True)
@click.option("--access-key", show_envvar=True)
@click.option("--secret-key", show_envvar=True)
@click.option("--cred-file", show_envvar=True)
@click.option("--region", show_envvar=True)
@click.option("--debug/--no-debug", default=False, show_envvar=True, show_default=True)
@click.pass_context
# pylint: disable = too-many-arguments
def iac_cmd(
    ctx,
    config_file,
    access_key,
    secret_key,
    cred_file,
    region,
    debug,
):  # noqa: R0913
    conf = iac.Config.from_toml(config_file, user_config_file_name())

    conf.debug = debug or conf.debug
    conf.region = region or conf.region
    conf.access_key = access_key or conf.access_key
    conf.secret_key = secret_key or conf.secret_key
    conf.cred_file = cred_file or conf.cred_file

    creds = None
    if conf.access_key and conf.secret_key:
        creds = iac.aws.Credentials(conf.access_key, conf.secret_key)
    elif conf.cred_file:
        creds = iac.get_credentials(conf.cred_file)

    ctx.obj["ec2"] = iac.make_ec2_client(creds, conf.region) if creds else None
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
    console(key, to_dict=iac.Key.to_dict)


@click.command(name="delete")
@click.pass_context
def key_delete_cmd(ctx):
    fail_on_debug(ctx)

    conf = ctx.obj["conf"]
    ec2 = ctx.obj["ec2"]

    kfm = iac.KeyFileManager(conf.secrets_folder)
    key = iac.delete_key_pair(ec2, kfm, conf.key_name)
    console(key, to_dict=iac.Key.to_dict)


@click.command(name="list")
@click.pass_context
def key_list_cmd(ctx):
    fail_on_debug(ctx)

    keys = iac.list_key_pairs(ctx.obj["ec2"])
    console(keys, to_dict=iac.Key.to_dict)


@click.command(name="dbgconf")
@click.pass_context
def x_dbgconf_cmd(ctx):
    fail_on_nodebug(ctx)

    console(ctx.obj["conf"], to_dict=iac.Config.to_dict)


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
    console(instance, to_dict=iac.Instance.to_dict)


@click.command(name="terminate")
@click.pass_context
def instance_terminate_cmd(ctx):
    fail_on_debug(ctx)

    instance = iac.terminate_instance(ctx.obj["ec2"], ctx.obj["conf"].instance_name)
    console(instance, to_dict=iac.Instance.to_dict)


@click.command(name="list")
@click.pass_context
def instance_list_cmd(ctx):
    fail_on_debug(ctx)

    instances = iac.list_instances(ctx.obj["ec2"])
    console(instances, to_dict=iac.Instance.to_dict)


iac_cmd.add_command(instance_cmd)
instance_cmd.add_command(instance_create_cmd)
instance_cmd.add_command(instance_terminate_cmd)
instance_cmd.add_command(instance_list_cmd)
instance_cmd.add_command(x_dbgconf_cmd)


@click.command(name="config")
def config_cmd():
    with open(sample_config_file_name(), encoding="utf8") as handle:
        console(handle.read())


iac_cmd.add_command(config_cmd)


def remote_runner(ctx):
    conf = ctx.obj["conf"]
    key_file = iac.KeyFileManager(conf.secrets_folder).key_file(conf.key_name)
    instance = iac.fetch_instance(ctx.obj["ec2"], conf.instance_name)
    return iac.RemoteCMDRunner.from_instance_and_key_file(instance, key_file)


@click.group(name="deploy")
@click.option("--instance-name", show_envvar=True)
@click.option("--key-name", show_envvar=True)
@click.option("--secrets-folder", show_envvar=True)
@click.pass_context
def deploy_cmd(ctx, instance_name, key_name, secrets_folder):
    conf = ctx.obj["conf"]

    conf.instance_name = instance_name or conf.instance_name
    conf.key_name = key_name or conf.key_name
    conf.secrets_folder = secrets_folder or conf.secrets_folder

    ctx.obj["conf"] = conf


@click.command(name="copy")
@click.argument("file_name")
@click.pass_context
def deploy_cmd_copy(ctx, file_name):
    fail_on_debug(ctx)

    remote_runner(ctx).copy(file_name)


@click.command(name="run")
@click.argument("cmd")
@click.pass_context
def deploy_cmd_run(ctx, cmd):
    fail_on_debug(ctx)

    out = remote_runner(ctx).run(cmd)
    console(out, to_dict=iac.run_result_to_dict)


iac_cmd.add_command(deploy_cmd)
deploy_cmd.add_command(deploy_cmd_copy)
deploy_cmd.add_command(deploy_cmd_run)
deploy_cmd.add_command(x_dbgconf_cmd)
