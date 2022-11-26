import json
import logging
import random
import string
import subprocess
import tempfile
import time

import pytest

LOGGER = logging.getLogger(__name__)


def info(msg):
    LOGGER.info(msg)


def warn(msg):
    LOGGER.warning(msg)


def run(cmd, log_cmd=False) -> dict:
    if log_cmd:
        info("  running:" + cmd)

    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


class NEDRunner:
    def __init__(self, ned_cmd, log_cmd=True):
        self.ned_cmd = ned_cmd
        self.log_cmd = log_cmd

    def __call__(self, *args, load_output=True) -> dict:
        cmd = self.ned_cmd + " " + " ".join(args)
        try:
            proc = run(cmd, log_cmd=self.log_cmd)
            assert proc.returncode == 0
        except subprocess.CalledProcessError as err:
            msg = "\n".join(
                [
                    "Subprocess failed execution.",
                    f"status {err.returncode}",
                    f"stdout:{err.stdout}",
                    f"stderr: {err.stderr}",
                ]
            )
            pytest.fail(msg)

        output = proc.stdout
        return json.loads(output) if output and load_output else {}


def test_ned_workflow__happy_path(pyned):
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-locals
    key_name = "bky-ned-live-test-key"
    instance_name = "bky-ned-live-test-instance"
    fqdn = "bky-ned-live-test-host.bky.sh"

    ned = NEDRunner(pyned)

    info("Check help commands")
    ned("deploy copy --help", load_output=False)
    ned("deploy run --help", load_output=False)
    ned("dns create --help", load_output=False)

    info("Checking initial state of keys")
    keys = ned("key list")
    initial_keys = {k["name"] for k in keys}

    if key_name in initial_keys:
        warn(f"Key {key_name} was found, attempting to remove")
        ned(f"key --key-name={key_name} delete")

        keys = ned("key list")
        initial_keys = {k["name"] for k in keys}

    assert key_name not in initial_keys

    info("Create key")
    ned(f"key --key-name={key_name} create")

    info("Checking key creation")
    keys = ned("key list")
    assert key_name in {k["name"] for k in keys}

    info("Checking initial state of instances")
    instances = ned("instance list")
    initial_instances = {i["name"] for i in instances}

    if instance_name in initial_instances:
        warn(f"Instance {instance_name} was found, attempting to terminate")
        ned(f"instance --key-name={key_name} --instance-name={instance_name} terminate")

        instances = ned("instance list")
        initial_instances = {i["name"] for i in instances}

    assert instance_name not in initial_instances

    info("Create instance")
    ned(f"instance --key-name={key_name} --instance-name={instance_name} --no-nitro create")

    info("Checking instance creation")
    instances = ned("instance list")
    assert instance_name in {i["name"] for i in instances}

    info("Checking initial state of DNS")
    records = ned(f"dns --fqdn={fqdn} list")
    initial_records = {r["fqdn"] for r in records}

    if fqdn in initial_records:
        warn(f"Record {fqdn} was found, attempting to delete")
        ned(f"dns --instance-name={instance_name} --fqdn={fqdn} delete")

        records = ned(f"dns --fqdn={fqdn} list")
        initial_records = {r["fqdn"] for r in records}

    assert fqdn not in initial_records

    info("Create DNS record")
    ned(f"dns --instance-name={instance_name} --fqdn={fqdn} create")

    info("Checking DNS record creation")
    record = ned(f"dns --fqdn={fqdn} describe")
    assert fqdn == record["fqdn"]

    info("Giving the system some time to startup")
    time.sleep(30)

    with tempfile.NamedTemporaryFile(prefix="bky-ned-") as tmp:
        junk = "".join(random.choices(string.ascii_lowercase, k=5))
        data = "Blocky Rocks!" + junk
        tmp.write(bytes(data, "utf-8"))
        tmp.flush()

        info("Copy file")
        ned(f"deploy --key-name={key_name} --instance-name={instance_name} copy {tmp.name}")

        path_on_remote = tmp.name.replace(tempfile.gettempdir(), ".")
        info("Run remote command")
        remote_result = ned(
            "deploy",
            f"--key-name={key_name}",
            f"--instance-name={instance_name}",
            f"run 'cat {path_on_remote}'",
        )
        assert remote_result["stdout"] == data

    info("Delete DNS record")
    ned(f"dns --instance-name={instance_name} --fqdn={fqdn} delete")

    info("Checking DNS deleted")
    records = ned(f"dns --fqdn={fqdn} list")
    assert fqdn not in records

    info("Terminate instance")
    ned(f"instance --key-name={key_name} --instance-name={instance_name} terminate")

    info("Checking instance termination")
    instances = ned("instance list")
    assert instance_name not in {i["name"] for i in instances}

    info("Delete key")
    ned(f"key --key-name={key_name} delete")

    info("Checking key deletion")
    keys = ned("key list")
    assert key_name not in {k["name"] for k in keys}

    info("Success!")
