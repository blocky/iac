from .context import gateway


def test_gateway(capsys):
    ret = gateway.Gateway.run()
    captured = capsys.readouterr()

    assert "Hello World..." in captured.out
    assert ret == 'Return content'
