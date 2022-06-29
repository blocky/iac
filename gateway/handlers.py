import datetime

from .models import Attestation, Heartbeat, HeartbeatStatus
from .serializers import HeartbeatSerializer, AddToSequenceSerializer, AttestationSerializer


class HeartbeatHandler:
    def run(self, _args: dict = None, _body: dict = None) -> dict:
        healthy = Heartbeat(HeartbeatStatus.HEALTHY)
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
