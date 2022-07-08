import datetime

from .models import (
    Attestation,
    Heartbeat,
    HeartbeatStatus,
)
from .serializers import (
    HeartbeatSerializer,
    AddToSequenceSerializer,
    AttestationSerializer,
    ConfigurationSerializer,
)


class HeartbeatHandler:
    def __init__(self, config):
        self.config = config

    def run(self, _args: dict = None, _body: dict = None) -> dict:
        config = ConfigurationSerializer().load_with_custom_error(self.config)
        healthy = Heartbeat(HeartbeatStatus.HEALTHY, config)
        return HeartbeatSerializer().dump(healthy)


class AddToSequenceHandler:
    def run(self, _args: dict = None, body: dict = None) -> dict:
        clean_body = AddToSequenceSerializer().load(body)

        fake_attestation = Attestation(
            data=clean_body["data"],
            idx=7,
            attestation="fake-attestation",
            created_at=datetime.datetime(2022, 6, 27, 17, 10),
        )

        return AttestationSerializer().dump(fake_attestation)
