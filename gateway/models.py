from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class HeartbeatStatus(Enum):
    HEALTHY = "healthy"


@dataclass
class Heartbeat:
    status: HeartbeatStatus


@dataclass
class Attestation:
    idx: int
    data: str
    attestation: str
    created_at: datetime
