"""Websocket client section for the Slurry stream processing microframework."""
__version__ = '0.2.9'

from trio_websocket import ConnectionClosed, ConnectionTimeout, HandshakeError, DisconnectionTimeout

from .websocket import Websocket
