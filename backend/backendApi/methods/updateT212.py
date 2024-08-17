import logging
from datetime import datetime, timezone
from time import time
from typing import List, Union

import ipdb
import pandas as pd
from bson import ObjectId
from fxrates import ExchangeRate

from admin.mongoDB import mongo_client
from classes.portfolio import Portfolio
from classes.securities import Fee, Order, Stock
from classes.users import User
from internalLibs.decorators import timing
from internalLibs.t212 import Trading212

logger = logging.getLogger("myapp")


@timing()
def init_client(client_id, ptf_index: int = 0):
    user = User(client_id, mongo_client=mongo_client)
    user.connect_user(fast_connect=True)
    ptf = Portfolio(
        mongo_client, user.ptf_ids[ptf_index] if user.ptf_ids else None
    )  # ptf[0] is always the 'basket ptf'
    if not user.ptf_ids:
        user.add_ptf_id(ptf._id)
    ptf.load()
    return ptf, user


@timing()
def init_format(orders: list, t212: Trading212, base_currency: str):
    instruments = t212.get_instruments(
        {"t212_id": list({order["t212_id"] for order in orders})}
    )
    instruments_dict = {instrument["t212_id"]: instrument for instrument in instruments}
    currencies = {
        instrument["currencyCode"]
        for instrument in instruments
        if instrument["currencyCode"] != base_currency
    }
    oldest_date = orders[-1]["dateModified"][:10]
    newest_date = orders[0]["dateModified"][:10]
    rates = ExchangeRate.convert(
        currencies, base_currency, date_from=oldest_date, date_to=newest_date
    )
    return instruments_dict, rates


@timing()
def format_orders(
    orders: list,
    ptf: Portfolio,
    rates: pd.DataFrame,
    instruments_dict: dict,
    base_currency: str,
):
    existing_stocks = {}
    for order in orders:
        # variables initialization
        t212_id = order["t212_id"]
        instrument = instruments_dict.get(t212_id)
        currency = instrument["currencyCode"]
        fees = []

        # process fees
        for fee in order["taxes"]:
            fees.append(Fee(fee["name"], fee["quantity"]))

        # process quantity
        if order["filledQuantity"] != None:
            quantity = order["filledQuantity"]
            quantity_estimated = False
        else:
            if base_currency != currency:
                try:
                    rate = rates.loc[order["dateModified"][:10], currency].item()
                except KeyError:
                    logger.warning(
                        f"{order['dateModified'][:10]} not found in rates dataframes. Rate switched to {rates.index[-1]}"
                    )
                    rate = rates.iloc[-1][currency].item()

            else:
                rate = 1
            quantity = (
                (order["filledValue"] + sum([fee.value for fee in fees]))
                * rate
                / order["fillPrice"]
            )
            quantity_estimated = True

        order_dict = {
            "broker": "T212",
            "date": datetime.strptime(order["dateModified"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "type": order["type"],
            "quantity": quantity,
            "quantity_estimated": quantity_estimated,
            "price": order["fillPrice"],
            "currency": currency,
            "fees": fees,
            "order_id": order["id"],
        }
        order_obj = Order(**order_dict)

        stock = existing_stocks.get(t212_id)
        if stock:
            stock.add_order(order_obj)
        else:
            stock_dict = {
                "isin": instrument["isin"],
                "ticker": instrument["ticker"],
                "t212_id": t212_id,
            }
            stock_obj = Stock(**stock_dict)
            stock_obj.add_order(order_obj)
            added_stock = ptf.add_security(stock_obj)
            existing_stocks[t212_id] = added_stock


def updateT212(client_id: Union[str, ObjectId], base_currency: str = "EUR"):
    ptf, user = init_client(client_id)
    t212 = Trading212(user.oaths["T212"], mongo_client)

    last_date = user.brokersLastUpdate.get("T212")
    # last_date = datetime.strptime('01/05/2024', '%d/%m/%Y')
    update_time = datetime.now(timezone.utc)
    orders = t212.get_orders(last_date, filter_func=lambda o: o["status"] == "FILLED")

    instruments_dict, rates = init_format(orders, t212, base_currency)
    orders = format_orders(orders, ptf, rates, instruments_dict, base_currency)
    ipdb.set_trace()
    ptf.push_securities("stocks")

    t = time()
    user._users_db.users.update_one(
        {"_id": user._id}, {"$set": {"brokersLastUpdate.T212": update_time}}
    )
    logger.info(f"T212 update date added to mongo in: {time() -t}")
    return orders
