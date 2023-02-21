# -*- coding: UTF-8 -*-

from logging import getLogger, Logger, StreamHandler, Formatter, DEBUG, INFO

from requests import Session, Response
from requests.adapters import HTTPAdapter
from requests_cache import install_cache
from requests_toolbelt.utils import dump
from urllib3.util.retry import Retry

from .authentication import SessionAuth
from .constants import CACHE
from .utils import decode


class TimeoutHTTPAdapter(HTTPAdapter):
    """Custom HTTP adapter with timeout capability."""

    def __init__(self, *args, **kwargs):
        self._timeout = kwargs.pop("timeout")
        super(TimeoutHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs.update({"timeout": self._timeout})
        return super(TimeoutHTTPAdapter, self).send(request, **kwargs)


class AuthSession(Session):
    """Base `Session` handler."""

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

    @staticmethod
    def timeout_http_adapter(retries: int, backoff: int, timeout: int) -> TimeoutHTTPAdapter:
        return TimeoutHTTPAdapter(
            max_retries=Retry(
                total=retries,
                backoff_factor=backoff
            ),
            timeout=timeout
        )

    def __init__(
            self,
            key: str,
            secret: str,
            cache: bool = True,
            retries: int = 3,
            backoff: int = 1,
            timeout: int = 30,
            debug: bool = False,
            logger: Logger = None
    ):
        """
        :param key: The API key;
        :param secret: The API secret;
        :param cache: Use caching (defaults to: `True`);
        :param retries: Total number of retries to allow (defaults to: 3).
        :param backoff: A backoff factor to apply between attempts after the
            second try (defaults to: 1).
        :param timeout: How long to wait for the server to send data before
            giving up (defaults to: 30).
        :param debug: Set to True to log all requests/responses to/from server
            (defaults to: ``False``).
        :param logger: The handler to be used for logging. If given, and level
            is above `DEBUG`, all debug messages will be ignored.
        """

        super(AuthSession, self).__init__()

        self.auth = SessionAuth(key, secret)

        self.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Accept-Charset": "utf-8",
            }
        )

        self.mount(
            "http://",
            self.timeout_http_adapter(retries, backoff, timeout)
        )

        self.mount(
            "https://",
            self.timeout_http_adapter(retries, backoff, timeout)
        )

        if cache is True:
            install_cache(cache_name=CACHE, backend="sqlite", expire_after=180)

        if debug is True:
            self.hooks["response"] = [self.debug]
            self._log.setLevel(DEBUG)
            self._console.setLevel(DEBUG)

        if logger is not None:
            self._log = logger

    def debug(self, response: Response, *args, **kwargs):
        data = dump.dump_all(response)
        self._log.debug(
            decode(data, encoding="UTF-8")
        )


__all__ = ["AuthSession"]
