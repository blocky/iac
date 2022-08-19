import dataclasses

import toml


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
    security_group: str = None

    @classmethod
    def from_toml(cls, config_file):
        aws = toml.load(config_file).get("iac").get("aws")
        return cls.from_kwargs(**aws)

    @classmethod
    def from_kwargs(cls, **kwargs):
        fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in kwargs.items() if k in fields})

    @staticmethod
    def to_dict(instance) -> dict:
        return instance.__dict__
