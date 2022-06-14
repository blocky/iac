import requests


def test_gateway_hello(capsys, example_fixture):
    r = requests.get('http://127.0.0.1:5000/')
    assert r.status_code == 200
    assert r.text == 'Return content'


def test_gateway_bad_endpoint(capsys, example_fixture):
    r = requests.get('http://127.0.0.1:5000/not-an-endpoint')
    assert r.status_code == 404
