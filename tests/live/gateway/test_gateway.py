import requests


def test_gateway_hello(gateway_fixture):
    r = requests.get("http://127.0.0.1:5000/")
    assert r.status_code == 200
    assert r.text == "Hello World..."


def test_gateway_bad_endpoint(gateway_fixture):
    r = requests.get("http://127.0.0.1:5000/not-an-endpoint")
    assert r.status_code == 404
