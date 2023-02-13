# -*- coding: UTF-8 -*-

from hashlib import sha256
from hmac import HMAC
from typing import List

from requests.auth import AuthBase
from requests.models import PreparedRequest
from requests.utils import to_native_string

from .utils import encode, decode, get_posix


class HMACBase(object):
    """Base HMAC authentication signature handler."""

    @staticmethod
    def _pre_hash(timestamp: str, method: str, path: str, body: str = None) -> str:
        """
        Create the pre-hash string by concatenating the timestamp with
        the request method, path and body if not None.
        """
        if body is not None:
            return f"{timestamp}{method}{path}{body}"
        return f"{timestamp}{method}{path}"

    @staticmethod
    def _sign(secret: str, message: str) -> str:
        """
        Create a sha256 HMAC and sign the required `message` using the
        API base64 decoded secret as `key`.
        """
        return HMAC(
            encode(secret, "UTF-8"),
            encode(message, "UTF-8"),
            digestmod=sha256
        ).hexdigest()

    @staticmethod
    def _headers(key: str, signature: str, timestamp: str) -> dict:
        return {
            "CB-ACCESS-KEY": to_native_string(key),
            "CB-ACCESS-SIGN": to_native_string(signature),
            "CB-ACCESS-TIMESTAMP": to_native_string(timestamp),
        }

    def __init__(self, key: str, secret: str):
        self.__key = key
        self.__secret = secret

    def _get_signature(self, method: str, path: str, body: str = None) -> dict:
        timestamp = str(int(get_posix()))
        message = self._pre_hash(
            timestamp=timestamp,
            method=method,
            path=path,
            body=body
        )
        return self._headers(
            key=self.__key,
            signature=self._sign(self.__secret, message),
            timestamp=timestamp,
        )


class SessionAuth(AuthBase, HMACBase):
    """Session HMAC authentication handler."""

    def __call__(self, request: PreparedRequest):
        self.sign(request)
        return request

    def sign(self, request: PreparedRequest):
        signature = self._get_signature(
            method=request.method.upper(),
            path=request.path_url.split("?")[0],
            body=decode(request.body, encoding="UTF-8")
        )
        request.headers.update(signature)


class WSAuth(object):

    @staticmethod
    def _pre_hash(timestamp: str, channel: str, product_ids: List[str]) -> str:
        return f"{timestamp}{channel}{','.join(product_ids)}"

    @staticmethod
    def _sign_message(secret: str, message: str) -> str:
        return HMAC(
            key=encode(secret, "UTF-8"),
            msg=encode(message, "UTF-8"),
            digestmod=sha256
        ).hexdigest()

    def __init__(self, key: str, secret: str):
        self._key = key
        self._secret = secret

    def sign(self, params: dict):
        timestamp = str(int(get_posix()))

        message = self._pre_hash(
            timestamp=timestamp,
            channel=params.get("channel"),
            product_ids=params.get("product_ids")
        )

        params.update(
            api_key=self._key,
            timestamp=timestamp,
            signature=self._sign_message(self._secret, message),
        )


__all__ = ["SessionAuth", "WSAuth"]
