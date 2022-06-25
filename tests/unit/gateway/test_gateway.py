from .context import gateway


def test_gateway():
    assert gateway.hello_world() == "Hello World..."
