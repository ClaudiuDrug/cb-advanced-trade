# -*- coding: UTF-8 -*-

from datetime import datetime, timezone
from queue import Queue
from typing import Union


def get_posix() -> float:
    """
    POSIX timestamp as float.
    Number of seconds since Unix Epoch in UTC.
    """
    utc = get_utc()
    return utc.timestamp()


def get_utc() -> datetime:
    """UTC as `datetime` object."""
    return datetime.now(timezone.utc)


def encode(value: Union[str, bytes], encoding: str = "UTF-8") -> bytes:
    """Encode the `value` using the codec registered for `encoding`."""
    if isinstance(value, str):
        return value.encode(encoding)
    return value


def decode(value: Union[bytes, str], encoding: str = "UTF-8") -> str:
    """Decode the `value` using the codec registered for `encoding`."""
    if isinstance(value, bytes):
        return value.decode(encoding)
    return value


class WSQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()

            try:
                if item is self.SENTINEL:  # exit signal
                    return
                yield item
            finally:
                self.task_done()


__all__ = ["get_posix", "encode", "decode", "WSQueue"]
