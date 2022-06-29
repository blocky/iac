import json

import requests

def test_gateway_404(gateway_fixture):
    r = requests.get("http://127.0.0.1:5000/not-an-endpoint")
    assert r.status_code == 404

    body = json.loads(r.text)
    assert body["error"].startswith("404 Not Found:")


def test_gateway_400_missing_args(gateway_fixture):
    r = requests.post("http://127.0.0.1:5000/sequence", json={})
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"] == "{'data': ['Missing data for required field.']}"


def test_gateway_400_extra_args(gateway_fixture):
    r = requests.post(
        "http://127.0.0.1:5000/sequence",
        json={"data": "abc123", "data2": "111"},
    )
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"] == "{'data2': ['Unknown field.']}"


def test_gateway_400_non_json_content_type(gateway_fixture):
    r = requests.post("http://127.0.0.1:5000/sequence", {"data":"abc123"})
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"].startswith("400 Bad Request")


def test_gateway_400_invalid_json(gateway_fixture):
    r = requests.post(
        "http://127.0.0.1:5000/sequence",
        data='{"data":"abc123"',
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"].startswith("400 Bad Request")


def test_gateway_heartbeat(gateway_fixture):
    r = requests.get("http://127.0.0.1:5000/heartbeat")
    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["status"] == "healthy"


def test_gateway_sequence(gateway_fixture):
    r = requests.post(
        "http://127.0.0.1:5000/sequence",
        json={"data": "abc123"},
    )
    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["attestation"] == "fake-attestation"
    assert body["created_at"] == "2022-06-27T17:10:00"
    assert body["data"] == "abc123"
    assert body["idx"] == 7
