# -*- coding: UTF-8 -*-

from os.path import dirname, join, realpath
from sys import modules

ROOT: str = dirname(realpath(modules["__main__"].__file__))

CACHE: str = join(ROOT, "cache", "cb_advanced_trade")

ADVANCED_TRADE: str = "api.coinbase.com"

API: str = "api/v3/brokerage"

MARKET_DATA: str = "advanced-trade-ws.coinbase.com"

ENDPOINTS: dict = {
    "Accounts": "accounts",
    "Orders": "orders",
    "Products": "products",
    "TransactionSummary": "transaction_summary",
}
