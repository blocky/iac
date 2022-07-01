import logging
import os
import signal
import subprocess
import time

import psutil
import pytest
from utils.utils import ROOT_PATH

LOGGER = logging.getLogger(__name__)


def terminate_process(parent_pid, sig=signal.SIGKILL):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)
    parent.send_signal(sig)


@pytest.fixture()
def gateway_fixture():
    LOGGER.info("Setting Up Gateway Fixture...")

    flask_env = os.environ.copy()
    flask_env["FLASK_APP"] = "gateway/gateway"

    proc = subprocess.Popen(
        "flask run".split(),
        env=flask_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT_PATH,
    )

    time.sleep(1)  # let flask start up for the test

    yield

    LOGGER.info("Tearing Down Gateway Fixture...")
    terminate_process(proc.pid)
