import json
from collections import defaultdict
from datetime import datetime
from time import time
from typing import TYPE_CHECKING, List, Literal

import pandas as pd
from fxrates import ExchangeRate

if TYPE_CHECKING:
    from classes.securities import Order, Stock


def get_stock_history(
    stocks: List["Stock"],
    date_from: str,
    date_to: str,
    interval: Literal["D", "W", "ME", "YE"],
    currency: str = "EUR",
):

    if date_to:
        now = datetime.now().strftime("%Y-%m-%d")
        if now < date_to:
            date_to = date_from
    dates = pd.date_range(start=date_from, end=date_to, freq=interval)
    data = defaultdict(lambda: defaultdict(lambda: {"Quantity": 0, "Book Value": 0}))

    tickers_list = []
    for stock in stocks:
        ticker = stock.ticker
        tickers_list.append(ticker)
        for order in stock.orders:
            order: "Order"
            order_date = pd.to_datetime(order.date)
            closest_date = dates[dates >= order_date].min()
            if pd.notna(closest_date):
                data[closest_date][ticker]["Quantity"] += order.quantity
                data[closest_date][ticker]["Book Value"] += order.price * order.quantity

    columns = pd.MultiIndex.from_product(
        [tickers_list, ["Quantity", "Book Value", "Market Value"]],
        names=["Ticker", "Metric"],
    )

    # Initialize the DataFrame with zeros
    df = pd.DataFrame(index=dates, columns=columns).fillna(0.0)

    # Populate the DataFrame
    for date, tickers in data.items():
        for ticker, values in tickers.items():
            df.at[date, (ticker, "Quantity")] = values["Quantity"]
            df.at[date, (ticker, "Book Value")] = values["Book Value"]

    # Set the index name
    df.index.name = "Date"

    df = df.apply(lambda x: x.cumsum())

    return {"YYYY-MM-DD": ["book_value", "market_value"]}
