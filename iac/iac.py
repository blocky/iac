from os.path import join
from pprint import pformat

import click
import toml
from environs import Env

import iac
from utils import utils


@click.group()
@click.option("--config-file")
@click.option("--access-key")
@click.option("--secret-key")
@click.option("--region")
@click.pass_context
def iac_cmd(ctx, config_file, access_key, secret_key, region):
    env = Env()
    env.read_env()

    if config_file is None:
        config_file = join(utils.config_path(), "config.toml")
    conf = toml.load(config_file)
    ctx.obj["aws"] = conf["iac"]["aws"]

    creds = iac.get_credentials(join(utils.secrets_path(), ctx.obj["aws"]["cred_file"]))

    if access_key is not None:
        ctx.obj["aws"]["access_key"] = access_key
    if secret_key is not None:
        ctx.obj["aws"]["secret_key"] = secret_key
    if region is not None:
        ctx.obj["aws"]["region"] = region

    ctx.obj["ec2"] = iac.make_ec2_client(creds, ctx.obj["aws"]["region"])


@click.group(name="key")
@click.option("-k", "--key-name")
@click.pass_context
def key_cmd(ctx, key_name):
    Env().read_env()
    if key_name is not None:
        ctx.obj["aws"]["key_name"] = key_name


@click.command(name="create")
@click.pass_context
def key_create_cmd(ctx):
    key = iac.create_key_pair(ctx.obj["ec2"], ctx.obj["aws"]["key_name"])
    print(f"Created key {key.name}")


@click.command(name="delete")
@click.pass_context
def key_delete_cmd(ctx):
    key = iac.delete_key_pair(ctx.obj["ec2"], ctx.obj["aws"]["key_name"])
    print(f"Deleted key {key.name}")


@click.command(name="list")
@click.pass_context
def key_list_cmd(ctx):
    print(f"Found keys \n{pformat(iac.list_key_pairs(ctx.obj['ec2']))}")


iac_cmd.add_command(key_cmd)
key_cmd.add_command(key_create_cmd)
key_cmd.add_command(key_delete_cmd)
key_cmd.add_command(key_list_cmd)


@click.group(name="instance")
@click.option("-i", "--instance-name")
@click.option("-k", "--key-name")
@click.option("-s", "--security-group")
@click.pass_context
def instance_cmd(ctx, instance_name, key_name, security_group):
    Env().read_env()
    if instance_name is not None:
        ctx.obj["aws"]["instance_name"] = instance_name
    if key_name is not None:
        ctx.obj["aws"]["key_name"] = key_name
    if security_group is not None:
        ctx.obj["aws"]["security_group"] = security_group


@click.command(name="create")
@click.pass_context
def instance_create_cmd(ctx):
    instance = iac.create_instance(
        ctx.obj["ec2"],
        ctx.obj["aws"]["instance_name"],
        ctx.obj["aws"]["key_name"],
        ctx.obj["aws"]["security_group"],
    )
    print(f"Created instance {instance.name} with id {instance.id}")


@click.command(name="terminate")
@click.pass_context
def instance_terminate_cmd(ctx):
    instance = iac.terminate_instance(ctx.obj["ec2"], ctx.obj["aws"]["instance_name"])
    print(f"Terminated instance {instance.name} with id {instance.id}")


@click.command(name="list")
@click.pass_context
def instance_list_cmd(ctx):
    print(f"Found instances \n{pformat(iac.list_instances(ctx.obj['ec2']))}")


iac_cmd.add_command(instance_cmd)
instance_cmd.add_command(instance_create_cmd)
instance_cmd.add_command(instance_terminate_cmd)
instance_cmd.add_command(instance_list_cmd)
