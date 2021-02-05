import pytest

import trio_websocket

from slurry_websocket import Websocket
from slurry import Pipeline


async def test_bitmex_testnet():
    with pytest.raises(trio_websocket.ConnectionRejected):
        async with Pipeline.create(
            Websocket('wss://testnet.bitmex.com/realtime', extra_headers=[
                ('api-expires', '0'),
                ('api-signature', '0'),
                ('api-key', '0')
            ])
        ) as pipeline, pipeline.tap() as aiter:
            async for item in aiter:
                assert False
