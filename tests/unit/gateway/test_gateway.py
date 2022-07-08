import json

from gateway import app


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_404(client):
    r = client.get("/not-an-endpoint")
    assert r.status_code == 404

    body = json.loads(r.text)
    assert body["error"].startswith("404 Not Found:")


def test_heartbeat__happy_path(client):
    r = client.get("/heartbeat")
    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["status"] == "healthy"
    assert set(body["configuration"].keys()) == {"JWT_ALGORITHM", "JWT_PUBLIC_KEY"}


def test_heartbeat__misconfigured(client):
    app.config["TESTING"] = True
    app.config["JWT_PUBLIC_KEY"] = None
    app.config["JWT_ALGORITHM"] = None
    with app.test_client() as client:
        r = client.get("/heartbeat")
        assert r.status_code == 500

        body = json.loads(r.text)
        assert body["error"] == {
            "JWT_ALGORITHM": ["Field may not be null."],
            "JWT_PUBLIC_KEY": ["Field may not be null."],
        }


def test_add_to_sequence__401_no_auth(client):
    r = client.post("/sequence", json={})
    assert r.status_code == 401

    body = json.loads(r.text)
    assert body["error"] == "Missing Authorization Header"


def test_add_to_sequence__422_bad_auth(client, token):
    r = client.post("/sequence", json={}, headers=auth(token + "a"))
    assert r.status_code == 422

    body = json.loads(r.text)
    assert body["error"] == "Signature verification failed"


def test_add_to_sequence__400_missing_args(client, token):
    r = client.post("/sequence", json={}, headers=auth(token))
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"] == {"data": ["Missing data for required field."]}


def test_add_to_sequence__400_extra_args(client, token):
    r = client.post(
        "/sequence",
        json={"data": "abc123", "data2": "111"},
        headers=auth(token),
    )
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"] == {"data2": ["Unknown field."]}


def test_add_to_sequence__400_non_json_content_type(client, token):
    r = client.post(
        "/sequence",
        data='{"data":"abc123}"',
        content_type="application/not-json",
        headers=auth(token),
    )
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"].startswith("400 Bad Request")


def test_add_to_sequence__400_invalid_json(client, token):
    r = client.post(
        "/sequence", data='{"data":"abc123"', content_type="application/json", headers=auth(token)
    )
    assert r.status_code == 400

    body = json.loads(r.text)
    assert body["error"].startswith("400 Bad Request")


def test_add_to_sequence__happy_path(client, token):
    r = client.post("/sequence", json={"data": "abc123"}, headers=auth(token))

    assert r.status_code == 200

    body = json.loads(r.text)
    assert body["attestation"] == "fake-attestation"
    assert body["created_at"] == "2022-06-27T17:10:00"
    assert body["data"] == "abc123"
    assert body["idx"] == 7
