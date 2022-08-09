from os.path import abspath, join, dirname

ROOT_PATH = dirname(abspath(join(__file__, "..")))


def config_path():
    return abspath(join(ROOT_PATH, "setup"))


def secrets_path():
    return abspath(join(ROOT_PATH, "secrets"))
