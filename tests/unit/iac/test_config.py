from .context import iac


def test_config__from_kwargs():
    region = "mars"
    access_key = "abc"
    secret_key = "123"

    config = iac.Config.from_kwargs(
        **{
            "region": region,
            "access_key": access_key,
            "secret_key": secret_key,
            "random": "junk",
        }
    )

    assert config.region == region
    assert config.access_key == access_key
    assert config.secret_key == secret_key
    assert config.cred_file is None
    assert config.key_name is None
    assert config.secrets_folder is None
    assert config.instance_name is None
    assert config.security_group is None
