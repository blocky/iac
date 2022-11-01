import os
import dataclasses
from typing import TypeVar

import toml

ConfigSelf = TypeVar("ConfigSelf", bound="Config")


@dataclasses.dataclass
# pylint: disable = too-many-instance-attributes
class Config:
    debug: bool = False
    region: str = None
    access_key: str = None
    secret_key: str = None
    cred_file: str = None
    key_name: str = None
    secrets_folder: str = None
    instance_name: str = None
    instance_kind: str = None
    security_group: str = None

    @classmethod
    def from_toml(cls, context: str, user: str) -> ConfigSelf:
        # pick the file to use for loading a config
        config_file = None
        if context is not None:
            config_file = context
        elif os.path.exists(user):
            config_file = user

        # get the "aws" portion of the config
        aws = {}
        if config_file:
            aws = toml.load(config_file).get("iac").get("aws")

        return cls.from_kwargs(**aws)

    @classmethod
    def from_kwargs(cls, **kwargs):
        fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in kwargs.items() if k in fields})

    @staticmethod
    def to_dict(config: ConfigSelf) -> dict:
        return config.__dict__
