# History

## v0.3.1

Previous versions of slurry-websocket would swallow connection closed exceptions, leaving the pipeline oblivious to remote closure
of the websocket. After experimenting with the consequences of this behaviour, it looks as if it would be more helpful to propagate
these events. This has the following consequences:

The pipeline will now raise ConnectionClosed, when the websocket section has it's underlying connection closed. This is propagated via the pump task that is running the section.

Any open Pipeline taps will close. No errors will be raised from taps. There isn't really any way to notify taps of errors, with any specificity. Taps are MemoryReceiveChannels and are effectively insulated from any errors that happen on the send side, by design.

* Fix: Revert pipeline closure handling.

## v0.2.10

* Simplify connection closure cleanup. Dead code removal and simpler logging.
* Update dependencies.

## v0.2.8

* Incorrect CloseReason import. This is purely used in type hinting and has no functional impact.

## v0.2.7

* Try to handle various websocket closure scenarios more cleanly, instead of throwing errors to the client.

## v0.2.6

* Add log messages to keep an eye on websocket status.

## v0.2.5

* Update to Slurry 0.10.1.

## v0.2.4

* Update to Slurry 0.9.0. Fix api changes.

## v0.2.3

* Update to Slurry 0.8.0.

## v0.2.1

* Decode orjson bytes-serialization to str before sending. Still twice as fast as ujson.

## v0.2.0

* Upgrade to trio-websocket 0.9.0
* Add proxies to underlying WebSocketConnection.
* Switch json serialiser/deserialiser to orjson.

## v0.1.8

Update to Slurry 0.6.0.

## v0.1.7

Update dependencies

## v0.1.6

Bump slurry version

## v0.1.5

Bump ujson version

## v0.1.0

First release