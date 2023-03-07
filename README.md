# cb-advanced-trade

Coinbase Advanced Trade API client library.

---

### Installation:

```commandline
python -m pip install [--upgrade] cb-advanced-trade
```

---

### Endpoints:

> ### INFO:
> Advanced Trade endpoints require authentication using an [API Key authentication](https://docs.cloud.coinbase.com/advanced-trade-api/docs/rest-api-auth) scheme.
> You can generate API keys [here](https://www.coinbase.com/settings/api).

* Accounts
* Orders
* Products
* TransactionSummary


**Required parameters:**
* `key`: str - The API key;
* `secret`: str - The API secret.

**Optional parameters:**
* `cache`: bool - Use caching (defaults to: `True`);
* `retries`: int - Total number of retries to allow (defaults to: `3`);
* `backoff`: int - A backoff factor to apply between attempts after the second try (defaults to: `1`);
* `timeout`: int - How long to wait for the server to send data before giving up (defaults to: `30`);
* `debug`: bool - Set to True to log all requests/responses to/from server (defaults to: `False`);
* `logger`: Logger - The handler to be used for logging (defaults to: `None`).

**Any of the endpoints can be instantiated or used as a context-manager:**

```python
from cb_advanced_trade import Accounts

credentials: dict = {
    "key": "KEY",
    "secret": "SECRET",
}  # be careful where you keep your credentials!


if __name__ == '__main__':

    endpoint = Accounts(**credentials)
    account = endpoint.get_account("2ca72458-ade9-45fd-83f2-e1f468b70026")
    endpoint.close()

    # or

    with Accounts(**credentials) as endpoint:
        account = endpoint.get_account("2ca72458-ade9-45fd-83f2-e1f468b70026")
```

---

### Resources:

For each mapped resource you must read the [documentation](https://docs.cloud.coinbase.com/advanced-trade-api/docs/welcome).
All the parameters these resources can take are described in the official documentation.

<details>
<summary>Accounts</summary>
<p>

* [get_accounts()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getaccounts)

  Get a list of authenticated accounts for the current user.


* [get_account()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getaccount)

  Get a list of information about an account, given an account UUID.

</p>
</details>

<details>
<summary>Orders</summary>
<p>

* [create_order()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder)

  Create an order with a specified `product_id` (asset-pair), `side` (buy/sell), etc.

  > #### **Maximum Open Orders Per Product**
  > The maximum number of `OPEN` orders you can have for a given `product_id` is 500. If you have 500 open orders for a
  > `product_id` at submission, new orders placed for that product enter a failed state immediately.


* [del_order()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_cancelorders)

  Initiate cancel requests for one or more orders.


* [get_orders()]()

  Get a list of orders filtered by optional query parameters (`product_id`, `order_status`, etc).

  > #### Maximum Open Orders Returned
  > The maximum number of `OPEN` orders returned is 1000.

  > #### CAUTION
  > If you have more than 1000 open, is recommended the
  > [WebSocket User channel](https://docs.cloud.coinbase.com/advanced-trade-api/docs/ws-channels#user-channel)
  > to retrieve all `OPEN` orders.


* [get_fills()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getfills)

  Get a list of fills filtered by optional query parameters (`product_id`, `order_id`, etc).


* [get_order()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorder)

  Get a single order by order ID.

</p>
</details>

<details>
<summary>Products</summary>
<p>

* [get_products()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproducts)

  Get a list of the available currency pairs for trading.  


* [get_product()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproduct)

  Get information on a single product by product ID.


* [get_product_candles()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getcandles)

  Get rates for a single product by product ID, grouped in buckets.


* [get_market_trades()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getmarkettrades)

  Get snapshot information, by product ID, about the last trades (ticks), best bid/ask, and 24h volume.

</p>
</details>

<details>
<summary>TransactionSummary</summary>
<p>

* [get_transaction_summary()](https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gettransactionsummary)

  Get a summary of transactions with fee tiers, total volume, and fees.

</p>
</details>

---

### Websocket client:

**Required parameters:**
* `key`: The API key;
* `secret`: The API secret;
* `channel`: The channel to subscribe to;
* `product_ids`: Product IDs as list of strings.

**Optional parameters:**
* `debug`: Set to True to log all requests/responses to/from server (defaults to: `False`).
* `logger`: The handler to be used for logging. If given, and level is above `DEBUG`,
  all debug messages will be ignored.


> **Note:**
> 
> For information about Websocket feed channels visit the
> [documentation](https://docs.cloud.coinbase.com/advanced-trade-api/docs/ws-channels).

### Examples:

<details>
<summary>MarketData</summary>
<p>

```python
from cb_advanced_trade import MarketData

credentials = {
"key": "YOUR KEY",
"secret": "YOUR SECRET",
}  # be careful where you keep this!


if __name__ == '__main__':

    client = MarketData(
        **credentials,
        channel="ticker",
        product_ids=["BTC-USD"],
        debug=True
    )

    client.listen()

    try:
        for tick in client.queue:
            print(tick)
    except KeyboardInterrupt:
        client.close()
```

</p>
</details>

---
