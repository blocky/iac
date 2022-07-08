from enum import Enum

from gateway.models import (
    values_as_strs,
    JWTAlgorithm,
    HeartbeatStatus,
)


def test_values_as_strs():
    class X(Enum):
        A = "a"
        B = "b"
        C = "c"

    assert values_as_strs(X) == ["a", "b", "c"]


def test_jwtalgorithm_str():
    assert "RS256" == str(JWTAlgorithm.RS256)
    assert "ES256" == str(JWTAlgorithm.ES256)


def test_heartbest_status_str():
    assert "healthy" == str(HeartbeatStatus.HEALTHY)
