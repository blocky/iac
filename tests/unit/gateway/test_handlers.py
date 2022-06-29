from gateway import handlers, models


def test_HeartbeatHandler_run():
    result = handlers.HeartbeatHandler().run()
    assert result["status"] == models.HeartbeatStatus.HEALTHY.value


def test_AddToSequenceHandler():
    body = {"data": "data-to-sign"}
    result = handlers.AddToSequenceHandler().run(body=body)
    assert result["attestation"] == "fake-attestation"
    assert result["created_at"] == "2022-06-27T17:10:00"
    assert result["data"] == "data-to-sign"
    assert result["idx"] == 7
