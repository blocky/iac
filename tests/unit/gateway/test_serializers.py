import pytest
from contextlib import nullcontext as does_not_raise

from gateway.serializers import (
    ConfigurationSerializer,
    ConfigurationLoadError,
    HeartbeatSerializer,
)
from gateway.models import (
    Configuration,
    Heartbeat,
    HeartbeatStatus,
    JWTAlgorithm,
)


def test_configuration_serializer__load_with_custom_error__missing_jwt_algorithm(flask_config):
    flask_config.pop(ConfigurationSerializer.JWT_ALGO_KEY)

    with pytest.raises(ConfigurationLoadError) as err:
        ConfigurationSerializer().load_with_custom_error(flask_config)

    want_messages = {"JWT_ALGORITHM": ["Missing data for required field."]}
    assert want_messages == err.value.messages


def test_configuration_serializer__load_with_custom_error__invalid_algo(flask_config):
    flask_config[ConfigurationSerializer.JWT_ALGO_KEY] = "not-a-valid-algo"

    with pytest.raises(ConfigurationLoadError) as err:
        ConfigurationSerializer().load_with_custom_error(flask_config)

    want_messages = {"JWT_ALGORITHM": ["Must be one of: RS256, ES256."]}
    assert want_messages == err.value.messages


def test_configuration_serializer__load_with_custom_error__missing_public_key(flask_config):
    flask_config.pop(ConfigurationSerializer.JWT_PUBLIC_KEY_KEY)

    with pytest.raises(ConfigurationLoadError) as err:
        ConfigurationSerializer().load_with_custom_error(flask_config)

    want_messages = {"JWT_PUBLIC_KEY": ["Missing data for required field."]}
    assert want_messages == err.value.messages


def test_configuration_serializer__load_with_custom_error__happy_path(flask_config):
    config = ConfigurationSerializer().load_with_custom_error(flask_config)
    assert config.jwt_algorithm == "RS256"
    assert config.jwt_public_key == "public_key"


def test_configuration_serializer__load_with_custom_error__ignore_extra_data(flask_config):
    with does_not_raise():
        flask_config["extra_junk"] = "should_be_ignored"
        ConfigurationSerializer().load_with_custom_error(flask_config)


def test_heartbeat_serializer__dump__happy_path(flask_config):
    heartbeat = Heartbeat(
        HeartbeatStatus.HEALTHY,
        Configuration(JWTAlgorithm.RS256, "abc123"),
    )
    data = HeartbeatSerializer().dump(heartbeat)
    assert data["status"] == "healthy"
    assert data["configuration"] == {"JWT_ALGORITHM": "RS256", "JWT_PUBLIC_KEY": "abc123"}
