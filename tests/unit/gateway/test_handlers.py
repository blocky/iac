import pytest

from gateway import handlers, models, serializers


def test_heartbeat_handler__run__happy_path(flask_config):
    result = handlers.HeartbeatHandler(flask_config).run()
    assert result["status"] == models.HeartbeatStatus.HEALTHY.value
    assert result["configuration"] == {
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": "public_key",
    }


def test_heartbeat_hander__run__misconfigured():
    with pytest.raises(serializers.ConfigurationLoadError) as e:
        handlers.HeartbeatHandler({}).run()
    assert str(e.value) == "Invalid configuration"


def test_add_to_sequence_handler__run__happy_path():
    body = {"data": "data-to-sign"}
    result = handlers.AddToSequenceHandler().run(body=body)
    assert result["attestation"] == "fake-attestation"
    assert result["created_at"] == "2022-06-27T17:10:00"
    assert result["data"] == "data-to-sign"
    assert result["idx"] == 7
