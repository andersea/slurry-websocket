import orjson
import pytest
import trio
from trio_websocket import serve_websocket, ConnectionClosed, open_websocket, connect_websocket

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
async def disconnecting_server():
    async def handler(request):
        ws = await request.accept()
        while True:
            try:
                await ws.send_message('bark')
                await trio.sleep(0.5)
                await ws.send_message('cart')
                await trio.sleep(0.5)
                await ws.send_message('suffer')
                await trio.sleep(0.5)
                await ws.send_message('impress')
                await trio.sleep(0.5)
                await ws.aclose(1000, 'Plug pulled.')
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

async def test_disconnect(disconnecting_server, autojump_clock):
    async def listener(tap):
        async for item in tap:
            assert item in {'bark', 'cart', 'suffer', 'impress'}
    try:
        async with Pipeline.create(
            Websocket.create('127.0.0.1', 49000, '/', use_ssl=False, parse_json=False) 
        ) as pipeline, trio.open_nursery() as nursery:
            nursery.start_soon(listener, pipeline.tap())
            nursery.start_soon(listener, pipeline.tap())
    except ConnectionClosed as cls:
        assert cls.reason.code == 1000
        assert cls.reason.reason == 'Plug pulled.'