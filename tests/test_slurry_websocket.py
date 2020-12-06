import orjson
import pytest
import trio
from trio_websocket import serve_websocket, ConnectionClosed, open_websocket, connect_websocket
import timeit

from slurry import Pipeline
from slurry_websocket import Websocket


@pytest.fixture
async def echo_server():
    async def handler(request):
        ws = await request.accept()
        while True:
            try:
                message = await ws.get_message()
                await ws.send_message(message)
            except ConnectionClosed:
                break
    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve_websocket, handler, '127.0.0.1', 49000, None)
        yield ('127.0.0.1', 49000)
        nursery.cancel_scope.cancel()

@pytest.fixture
def hello_world():
    return {
        'message': 'hello, world',
        'number': 42
    }

def test_websocket_init():
    assert isinstance(Websocket('wss://dummy'), Websocket)

async def test_websocket_create():
    assert isinstance(Websocket.create('127.0.0.1', 49000, '', use_ssl=False), Websocket)

async def test_json(echo_server, hello_world):
    send_channel, receive_channel = trio.open_memory_channel(1)
    async with Pipeline.create(
        receive_channel,
        Websocket.create('127.0.0.1', 49000, '/', use_ssl=False, parse_json=True) 
    ) as pipeline, pipeline.tap() as tap:
        await send_channel.send(hello_world)
        response = await tap.receive()
        assert 'message' in response
        assert response['message'] == 'hello, world'

async def test_binary(echo_server, hello_world):
    send_channel, receive_channel = trio.open_memory_channel(1)
    async with Pipeline.create(
        receive_channel,
        Websocket.create('127.0.0.1', 49000, '/', use_ssl=False, parse_json=False) 
    ) as pipeline, pipeline.tap() as tap:
        message = orjson.dumps(hello_world)
        await send_channel.send(message)
        response = await tap.receive()
        assert isinstance(response, bytes)
        assert response == message
