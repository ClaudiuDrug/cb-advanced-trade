# -*- coding: UTF-8 -*-

from json import loads, dumps
from logging import getLogger, Logger, StreamHandler, Formatter, DEBUG, INFO
from threading import Thread
from typing import List

from websocket import WebSocketApp

from .authentication import WSAuth
from .constants import MARKET_DATA
from .utils import WSQueue


class MarketData(object):
    """Websocket client session handler."""

    # create a logger and set level to debug:
    _log: Logger = getLogger(__name__)
    _log.setLevel(INFO)

    # create console handler and set level to debug:
    _console = StreamHandler()
    _console.setLevel(INFO)

    # create formatter:
    _formatter = Formatter(
        "[%(asctime)s] - %(levelname)s - <%(filename)s, %(lineno)d, %(funcName)s>: %(message)s"
    )

    # add formatter to console:
    _console.setFormatter(_formatter)

    # add console to logger:
    _log.addHandler(_console)

    def __init__(
            self,
            key: str,
            secret: str,
            channel: str,
            product_ids: List[str],
            debug: bool = False,
            logger: Logger = None,
    ):
        """
        :param key: The API key;
        :param secret: The API secret;
        :param channel: The channel to subscribe to.
        :param product_ids: Product IDs as list of strings.
        :param debug: Set to True to log all requests/responses to/from server
            (defaults to: `False`).
        :param logger: The handler to be used for logging. If given, and level
            is above `DEBUG`, all debug messages will be ignored.
        """
        self._hmac = WSAuth(key=key, secret=secret)
        self._channel = channel
        self._product_ids = product_ids
        self._queue = WSQueue()

        if debug is True:
            self._log.setLevel(DEBUG)
            self._console.setLevel(DEBUG)

        if logger is not None:
            self._log = logger

        self._log.debug("Creating a new websocket client instance...")

        self._websocket = WebSocketApp(
            url=f"wss://{MARKET_DATA}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    @property
    def queue(self) -> WSQueue:
        return self._queue

    def listen(self, *args, **kwargs):
        """Start the listener."""
        thread = Thread(
            target=self._websocket.run_forever,
            name="websocket",
            args=args,
            kwargs=kwargs
        )
        thread.start()
        self._log.debug("Listening for websocket client messages...")

    def close(self):
        self.unsubscribe(self._websocket)
        self._websocket.close()
        self._queue.close()

    def on_open(self, websocket: WebSocketApp):
        """Action taken on websocket open event."""
        self.subscribe(websocket)

    def on_message(self, websocket: WebSocketApp, message: str):
        """Action taken for each message received."""
        message = loads(message)

        if message.get("type").lower() == "error":
            self._log.error(f"{message.get('message')}! {message.get('reason')}!")
            self.close()

        self._queue.put(message)

    def on_close(self, websocket: WebSocketApp, status, reason):
        """Action taken on websocket close event."""
        self._log.debug("The websocket client instance was terminated.")

    def on_error(self, websocket: WebSocketApp, exception):
        """Action taken when exception occurs."""
        self._log.error("Websocket client failed!", exc_info=exception)

    def subscribe(self, websocket: WebSocketApp):
        self._log.debug(
            f"Subscribing to channel '{self._channel}' "
            f"for product ids '{', '.join(self._product_ids)}'..."
        )
        params = {
            "type": "subscribe",
            "channel": self._channel,
            "product_ids": self._product_ids,
        }
        self._hmac.sign(params)
        websocket.send(dumps(params))

    def unsubscribe(self, websocket: WebSocketApp):
        self._log.debug(
            f"Unsubscribing from channel '{self._channel}' "
            f"for product ids '{', '.join(self._product_ids)}'..."
        )
        params = {
            "type": "unsubscribe",
            "channel": self._channel,
            "product_ids": self._product_ids,
        }
        websocket.send(dumps(params))


__all__ = ["MarketData"]
