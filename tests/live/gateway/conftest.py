import logging
import os
import signal
import subprocess
import time

import psutil
import pytest
from utils.utils import ROOT_PATH

from gateway import auth

LOGGER = logging.getLogger(__name__)

ZPR_CHAIN_ID = "chain-name"
ZPR_JWT_ALGO = "RS256"
ZPR_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""
ZPR_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAyT6kCdnoka7Qu9yn0NOn
RF3ZjVQ6CVSEQEjnNJY5MEG3LVc0TR9r1CtYS9XOxw0KOZQ0u2Nt9kwHNqSegdu4
utJ0iVu44nuHL+kbwbvM07PVlNFOT6LBeLk2PN6r9HW1riu+aMV7JwiO6ry6gEOs
tzwIznmNfJmUEFaOSFbXoNUTW2tHJe0YnNOdYR9qG1x+g3mpKF+3hcBMDwBMYfU2
sa7+GgfD99LTUcma0o5Mo3YekhhmucT1R0PfsHT6j/H0BFMAOKAL+ZKeawsBO7yv
usABUts7jVMd1qOxQ4fOUgE1+3ErKpg8BiATnLJHiFWEWo+Cw0qbq3ubHNWEdtiw
N+XYzNB0YCW8vs8KprbSiy0xALWdULdy3Ea0AkUNhfcI2D+ewXU0CMVEYxdOb6Ae
3xcpRnFeiyHPPdDEuFQUjealpCViHA2YiUFCiI6RXyNVNgdpjXboDORAPbWxIeTP
InZtgvx2pBhVL0ZbrszSVBohVULDlJl/x2VThXALPqU0B2KgdwRlaIv6TPjmqqQR
hEIZp8jm0itmCFdx2ddAjDOBRxj+cbK5A4Rwn62lyRd3D37Y2I+bMuS91RPFaZ3I
kJT1HrIDDECeieBXEe6iqZ5HTiD6/4uUhXvi5hTFkt+/GKvJtXgel+GELFo4RhCk
tpYI879omhjckYrGfVkhIEMCAwEAAQ==
-----END PUBLIC KEY-----
"""


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
    flask_env["BKY_SEQ_GATEWAY_JWT_PUBLIC_KEY"] = ZPR_PUBLIC_KEY
    flask_env["BKY_SEQ_GATEWAY_JWT_ALGORITHM"] = ZPR_JWT_ALGO

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


@pytest.fixture
def token():
    return auth.make_token(ZPR_CHAIN_ID, ZPR_PRIVATE_KEY, ZPR_JWT_ALGO)
