from slurry_websocket import Websocket


def test_version():
    assert isinstance(Websocket(), Websocket)
