from datetime import datetime
from dataclasses import dataclass
from enum import Enum, unique


def values_as_strs(enum: Enum):
    return [str(e.value) for e in enum]


class _StrAsValMixin:
    def __str__(self) -> str:
        return self.value


class JWTAlgorithm(_StrAsValMixin, Enum):
    RS256 = "RS256"
    ES256 = "ES256"


@dataclass
class Configuration:
    jwt_algorithm: str
    jwt_public_key: str


@unique
class HeartbeatStatus(_StrAsValMixin, Enum):
    HEALTHY = "healthy"


@dataclass
class Heartbeat:
    status: HeartbeatStatus
    configuration: Configuration


@dataclass
class Attestation:
    idx: int
    data: str
    attestation: str
    created_at: datetime
