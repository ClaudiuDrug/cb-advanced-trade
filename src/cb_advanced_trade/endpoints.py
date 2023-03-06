# -*- coding: UTF-8 -*-

from abc import ABC
from json import JSONDecodeError
from typing import List

from requests import Response, HTTPError

from .constants import API, ADVANCED_TRADE, ENDPOINTS
from .sessions import AuthSession


class AdvancedTrade(ABC):
    """Advanced Trade API authenticated base endpoint."""

    _url = f"https://{ADVANCED_TRADE}/{API}"

    @staticmethod
    def _join(*args, **kwargs) -> str:
        """
        Construct  an url address using `args` for path and `kwargs` as
        query params if given.
        """
        url = "/".join(args)
        if len(kwargs) > 0:
            url = f"{url}?{'&'.join(f'{key}={value}' for key, value in kwargs.items())}"
        return url

    @staticmethod
    def _error_side(status: int) -> str:
        if 400 <= status < 500:
            return "Client"

        if 500 <= status < 600:
            return "Server"

    def __init__(self, key: str, secret: str, **kwargs):
        """
        **Parameters:**
            - ``key``: The API key;
            - ``secret``: The API secret;
            - ``cache``: Use caching (defaults to: `True`);
            - ``retries``: Total number of retries to allow (defaults to: 3);
            - ``backoff``: A backoff factor to apply between attempts after
              the second try (defaults to: 1);
            - ``timeout``: How long to wait for the server to send data before
              giving up (defaults to: 30);
            - ``debug``: bool - Set to True to log all requests/responses
              to/from server (defaults to: `False`).
            - ``logger``: Logger - The handler to be used for logging.
              If given, and level is above `DEBUG`, all debug messages will be
              ignored.
        """
        self._session = AuthSession(key, secret, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Closes all adapters and as such the session"""
        self._session.close()

    def _get_endpoint_name(self) -> str:
        return ENDPOINTS.get(self.__class__.__name__)

    def _get(self, *args, **kwargs):
        return self._request(self._session.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request(self._session.post, *args, **kwargs)

    def _request(self, method, *args, **kwargs):
        kwargs.update(
            url=self._join(self._url, self._get_endpoint_name(), *args)
        )
        response = method(**kwargs)
        if response.status_code != 200:
            self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: Response):
        try:
            error: dict = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        else:
            status: int = response.status_code
            message: str = error.get("message").rstrip(".?!")
            side: str = self._error_side(status)

            if message is None:
                message: str = response.reason or "Unknown"

            raise HTTPError(
                f"{status} {side} Error: {message}! URL: {response.url}"
            )


class Accounts(AdvancedTrade):
    """`accounts` endpoint of the Advanced Trade API"""

    def get_accounts(self, **kwargs) -> dict:
        """
        Get a list of authenticated accounts for the current user.

        **kwargs:**

            - ``limit``: int - A pagination limit with default of 49 and
              maximum of 250. If has_next is true, additional orders are
              available to be fetched with pagination and the cursor value
              in the response can be passed as cursor parameter in the
              subsequent request.
            - ``cursor``: str - Cursor used for pagination. When provided,
              the response returns responses after this cursor.
        """
        return self._get(params=kwargs)

    def get_account(self, account_uuid: str) -> dict:
        """
        Get a list of information about an account, given an account UUID.

        :param account_uuid: The account's UUID.
        """
        return self._get(account_uuid)


class Orders(AdvancedTrade):
    """`orders` endpoint of the Advanced Trade API"""

    def create_order(self, client_order_id: str, product_id: str, side: str, **kwargs) -> dict:
        """
        Create an order with a specified `product_id` (asset-pair),
        `side` (buy/sell), etc.

        **Maximum Open Orders Per Product**
            The maximum number of `OPEN` orders you can have for a given
            `product_id` is 500. If you have 500 open orders for a `product_id`
            at submission, new orders placed for that product enter a failed
            state immediately.

        **kwargs:**
            - ``client_order_id``: Client set unique uuid for this order

            - ``product_id``: The product this order was created for
              e.g. 'BTC-USD'

            - ``side``: Possible values: `UNKNOWN_ORDER_SIDE`, `BUY` or `SELL`

            - ``order_configuration``: dict

                - ``market_market_ioc``: dict

                    - ``quote_size``: str - Amount of quote currency to spend
                      on order. Required for `BUY` orders.

                    - ``base_size``: str - Amount of base currency to spend on
                      order. Required for `SELL` orders.

                - ``limit_limit_gtc``: dict

                    - ``base_size``: str - Amount of base currency to spend on
                      order.

                    - ``limit_price``: str - Ceiling price for which the order
                      should get filled.

                    - ``post_only``: bool - Post only limit order.

                - ``limit_limit_gtd``: dict

                    - ``base_size``: str - Amount of base currency to spend on
                      order.

                    - ``limit_price``: str - Ceiling price for which the order
                      should get filled.

                    - ``end_time``: str - Time at which the order should be
                      cancelled if it's not filled.

                      i.e. `2023-02-03T13:06`

                    - ``post_only``: bool - Post only limit order.

                - ``stop_limit_stop_limit_gtc``: dict

                    - ``base_size``: str - Amount of base currency to spend on
                      order.

                    - ``limit_price``: str - Ceiling price for which the order
                      should get filled.

                    - ``stop_price``: str - Price at which the order should
                      trigger - if stop direction is Up, then the order will
                      trigger when the last trade price goes above this,
                      otherwise order will trigger when last trade price goes
                      below this price.

                    - ``stop_direction``: str - Possible values:

                        - UNKNOWN_STOP_DIRECTION
                        - STOP_DIRECTION_STOP_UP
                        - STOP_DIRECTION_STOP_DOWN

                - ``stop_limit_stop_limit_gtd``: dict

                    - ``base_size``: str - Amount of base currency to spend on
                      order.

                    - ``limit_price``: str - Ceiling price for which the order
                      should get filled.

                    - ``stop_price``: str - Price at which the order should
                      trigger - if stop direction is Up, then the order will
                      trigger when the last trade price goes above this,
                      otherwise order will trigger when last trade price goes
                      below this price.

                    - ``end_time``: str - Time at which the order should be
                      cancelled if it's not filled.

                      i.e. `2023-02-23T12:05`

                    - ``stop_direction``: str - Possible values:

                        - UNKNOWN_STOP_DIRECTION
                        - STOP_DIRECTION_STOP_UP
                        - STOP_DIRECTION_STOP_DOWN
        """
        kwargs.update(
            client_order_id=client_order_id,
            product_id=product_id,
            side=side,
        )
        return self._post(json=kwargs)

    def del_order(self, order_ids: List[str]) -> dict:
        """
        Initiate cancel requests for one or more orders.

        :param order_ids: The IDs of orders cancel requests should be
            initiated for.
        """
        return self._post(
            "batch_cancel",
            json={"order_ids": order_ids}
        )

    def get_orders(self, **kwargs) -> dict:
        """
        Get a list of orders filtered by optional query parameters
        (`product_id`, `order_status`, etc).

        **Maximum Open Orders Returned**
            The maximum number of `OPEN` orders returned is 1000.

        **CAUTION**
            If you have more than 1000 open, we recommend the WebSocket User
            channel to retrieve all `OPEN` orders.

        **kwargs:**
            - ``product_id``: str - Optional string of the product ID.
              Defaults to null, or fetch for all products.

            - ``order_status``: List[str] - A list of order statuses.

            - ``limit``: int - A pagination limit with no default set.
              If `has_next` is true, additional orders are available to be
              fetched with pagination; also the `cursor` value in the response
              can be passed as `cursor` parameter in the subsequent request.

            - ``start_date``: str - Start date to fetch orders from,
              inclusive.

            - ``end_date``: str - An optional end date for the query window,
              exclusive. If provided only orders with creation time before
              this date will be returned.

            - ``user_native_currency``: str - String of the users native
              currency. Default is USD.

            - ``order_type``: str - Type of orders to return.
              Default is to return all order types.

                - ``MARKET``: A market order;
                - ``LIMIT``: A limit order;
                - ``STOP``: A stop order is an order that becomes a market
                  order when triggered;
                - ``STOP_LIMIT``: A stop order is a limit order that doesn't
                  go on the book until it hits the stop price.
                - ``UNKNOWN_ORDER_TYPE``

            - ``order_side``: str - Only orders matching this side are
              returned. Default is to return all sides.

                - BUY
                - SELL
                - UNKNOWN_ORDER_SIDE

            - ``cursor``: str - Cursor used for pagination. When provided, the
              response returns responses after this cursor.

            - ``product_type``: str - Only orders matching this product type
              are returned. Default is to return all product types.
        """
        if "limit" not in kwargs:
            kwargs.update(limit=100)
        return self._get("historical", "batch", params=kwargs)

    def get_fills(self, **kwargs) -> dict:
        """
        Get a list of fills filtered by optional query parameters
        (`product_id`, `order_id`, etc).

        **kwargs:**
            - ``order_id``: str - ID of order;

            - ``product_id``: str - The ID of the product this order was
              created for;

            - ``start_sequence_timestamp``: str - Start date. Only fills
              with a trade time at or after this start date are returned;

            - ``end_sequence_timestamp``: str - End date. Only fills with a
              trade time before this start date are returned;

            - ``limit``: int - Maximum number of fills to return in response.
              Defaults to 100;

            - ``cursor``: str - Cursor used for pagination. When provided,
              the response returns responses after this cursor.
        """
        return self._get("historical", "fills", params=kwargs)

    def get_order(self, order_id: str, **kwargs) -> dict:
        """
        Get a single order by order ID.

        **Parameters:**
            - ``order_id``: str - The ID of the order to retrieve.

            - ``client_order_id``: str - Deprecated!
              Client Order ID to fetch the order with.

            - ``user_native_currency``: str - Deprecated!
              User native currency to fetch order with.
        """
        return self._get("historical", order_id, params=kwargs)


class Products(AdvancedTrade):
    """ `products` endpoint of the Advanced Trade API."""

    def get_products(self, **kwargs) -> dict:
        """
        Get a list of the available currency pairs for trading.

        **kwargs:**
            - ``limit``: int - A limit describing how many products to return.

            - ``offset``: int - Number of products to offset before returning.

            - ``product_type``: str - Type of products to return.

                - SPOT
        """
        return self._get(params=kwargs)

    def get_product(self, product_id: str) -> dict:
        """
        Get information on a single product by product ID.

        :param product_id: The trading pair to get information for.
        """
        return self._get(product_id)

    def get_product_candles(self, product_id: str, start: str, end: str, granularity: str) -> dict:
        """
        Get rates for a single product by product ID, grouped in buckets.

        :param product_id: The trading pair.
        :param start: Timestamp for starting range of aggregations,
            in UNIX time.
        :param end: Timestamp for ending range of aggregations,
            in UNIX time.
        :param granularity: The time slice value for each candle.
            Accepted values: [
                ONE_MINUTE,
                FIVE_MINUTE,
                FIFTEEN_MINUTE,
                THIRTY_MINUTE,
                ONE_HOUR,
                TWO_HOUR,
                SIX_HOUR,
                ONE_DAY
            ]
        """
        return self._get(
            product_id,
            "candles",
            params={
                "start": start,
                "end": end,
                "granularity": granularity
            }
        )

    def get_market_trades(self, product_id: str, limit: int = 100):
        """
        Get snapshot information, by product ID, about the last trades (ticks),
        best bid/ask, and 24h volume.

        :param product_id:
        :param limit:
        :return:
        """
        return self._get(
            product_id,
            "ticker",
            params={"limit": limit}
        )


class TransactionSummary(AdvancedTrade):
    """`transaction_summary` endpoint of the Advanced Trade API."""

    def get_transaction_summary(self, **kwargs) -> dict:
        """
        Get a summary of transactions with fee tiers, total volume, and fees.

        **kwargs:**
            - ``start_date``: str

            - ``end_date``: str

            - ``user_native_currency``: str - String of the users native currency, default is USD

            - ``product_type``: str - Type of product (i.e. `SPOT`).
        """
        return self._get(params=kwargs)


__all__ = [
    "Accounts",
    "Orders",
    "Products",
    "TransactionSummary",
]
