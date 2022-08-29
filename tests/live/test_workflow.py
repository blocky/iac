import json
import logging
import os
import subprocess

LOGGER = logging.getLogger(__name__)


def info(msg):
    LOGGER.info(msg)


def warn(msg):
    LOGGER.warning(msg)


class IACRunner:
    def __init__(self, iac_cmd):
        self.iac_cmd = iac_cmd

    def __call__(self, args, log=False) -> dict:
        env = os.environ.copy()

        cmd = self.iac_cmd + " " + args

        info("  running:" + cmd)

        proc = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            env=env,
        )
        assert proc.returncode == 0
        assert proc.stderr == ""

        output = proc.stdout
        if log:
            info(output)

        return json.loads(output)


def test_iac_workflow__happy_path(pyiac):
    key_name = "bky-iac-live-test-key"
    instance_name = "bky-iac-live-test-instance"

    iac = IACRunner(pyiac)

    info("Checking initial state of keys")
    keys = iac("key list")
    initial_keys = {k["name"] for k in keys}

    if key_name in initial_keys:
        warn(f"Key {key_name} was found, attempting to remove")
        iac(f"key --key-name={key_name} delete")

        keys = iac("key list")
        initial_keys = {k["name"] for k in keys}

    assert key_name not in initial_keys

    info("Create key")
    iac(f"key --key-name={key_name} create")

    info("Checking key creation")
    keys = iac("key list")
    assert key_name in {k["name"] for k in keys}

    info("Checking initial state of instances")
    instances = iac("instance list")
    initial_instances = {i["name"] for i in instances}

    if instance_name in initial_instances:
        warn(f"Instance {instance_name} was found, attempting to terminate")
        iac(f"instance --key-name={key_name} --instance-name={instance_name} terminate")

        instances = iac("instance list")
        initial_instances = {i["name"] for i in instances}

    assert instance_name not in initial_instances

    info("Create instance")
    iac(f"instance --key-name={key_name} --instance-name={instance_name} create")

    info("Checking instance creation")
    instances = iac("instance list")
    assert instance_name in {i["name"] for i in instances}

    info("Terminate instance")
    iac(f"instance --key-name={key_name} --instance-name={instance_name} terminate")

    info("Checking instance termination")
    instances = iac("instance list")
    assert instance_name not in {i["name"] for i in instances}

    info("Delete key")
    iac(f"key --key-name={key_name} delete")

    info("Checking key deletion")
    keys = iac("key list")
    assert key_name not in {k["name"] for k in keys}

    info("Success!")
