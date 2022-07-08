import json

import requests


def test_gateway_heartbeat(gateway_fixture):
    r = requests.get("http://127.0.0.1:5000/heartbeat")
    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["status"] == "healthy"


def test_gateway_sequence(gateway_fixture, token):
    r = requests.post(
        "http://127.0.0.1:5000/sequence",
        json={"data": "abc123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["attestation"] == "fake-attestation"
    assert body["created_at"] == "2022-06-27T17:10:00"
    assert body["data"] == "abc123"
    assert body["idx"] == 7
