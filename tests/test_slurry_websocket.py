import pytest
import trio
from trio_websocket import serve_websocket, ConnectionClosed, open_websocket, connect_websocket

from slurry import Pipeline
from slurry_websocket import Websocket

@pytest.fixture
def echo_server():
    async def _echo_server(request):
        ws = await request.accept()
        while True:
            try:
                message = await ws.get_message()
                await ws.send_message(message)
            except ConnectionClosed:
                break
    return _echo_server

def test_websocket_init():
    assert isinstance(Websocket('wss://dummy'), Websocket)

async def test_websocket_create():
    assert isinstance(Websocket.create('127.0.0.1', 49000, '', use_ssl=False), Websocket)

async def test_echo(echo_server):
    hello_world = {
        'message': 'hello, world'
    }
    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve_websocket, echo_server, '127.0.0.1', 49000, None)

        send_channel, receive_channel = trio.open_memory_channel(1)
        async with Pipeline.create(
            receive_channel,
            Websocket.create('127.0.0.1', 49000, '/', use_ssl=False, parse_json=True) 
        ) as pipeline, pipeline.tap() as tap:
            await send_channel.send(hello_world)
            response = await tap.receive()
            assert 'message' in response
            assert response['message'] == 'hello, world'
        nursery.cancel_scope.cancel()
