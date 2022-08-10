import os
from os.path import abspath, join


def config_path():
    cwd = os.getcwd()
    return abspath(join(cwd, "setup"))
