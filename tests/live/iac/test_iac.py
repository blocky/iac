import logging
import os
import subprocess

from utils.utils import ROOT_PATH

LOGGER = logging.getLogger(__name__)


def run(cmd: str, env: dict = None, prepend: str = "") -> str:
    if env is None:
        env = os.environ.copy()

    if "PYCHARM_HOSTED" in env:
        env["PATH"] = env["CONDA_PATH"] + ":" + env["PATH"]
        cmd = "conda run -n sequencer " + cmd

    cmd = prepend + " " + cmd

    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        env=env,
        cwd=ROOT_PATH,
    )
    assert proc.returncode == 0
    assert proc.stderr == ""
    return str(proc.stdout.strip())


def test_iac_workflow__happy_path():
    LOGGER.info(run("python -m iac key create"))
    assert "[]" != run("python -m iac key list")

    LOGGER.info(run("python -m iac instance create"))
    assert "[]" != run("python -m iac instance list")

    LOGGER.info(run("python -m iac instance terminate"))
    assert "[]" == run("python -m iac instance list")

    LOGGER.info(run("python -m iac key delete"))
    assert "[]" == run("python -m iac key list")
