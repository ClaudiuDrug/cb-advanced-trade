# -*- coding: UTF-8 -*-

from os.path import dirname, join, realpath
from sys import modules

ROOT: str = dirname(realpath(modules["__main__"].__file__))

ENVIRONMENT: str = "production"  # or: "sandbox"

CACHE: str = join(ROOT, "cache", "cb_advanced_trade")

VERSION: str = "2021-08-27"

API: str = "api/v3/brokerage"

ADVANCED_TRADE: dict = {
    "production": "api.coinbase.com",
}

MARKET_DATA: dict = {
    "production": "advanced-trade-ws.coinbase.com",
}

ENDPOINTS: dict = {
    "Accounts": "accounts",
    "Orders": "orders",
    "Products": "products",
    "TransactionSummary": "transaction_summary",
}
