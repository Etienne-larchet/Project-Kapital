import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List, Literal, Optional

from .generals import GeneralMethods

if TYPE_CHECKING:
    from bson import ObjectId
    from pymongo import MongoClient


@dataclass
class Fee:
    type: str
    value: int


class Order(GeneralMethods):
    def __init__(
        self,
        broker: Optional[Literal["T212", "IBKR", "TR"]] = None,
        type: Optional[Literal["LIMIT", "MARKET"]] = None,
        quantity: Optional[float] = None,
        quantity_estimated: bool = False,
        price: Optional[float] = None,
        date: Optional[datetime] = None,
        order_id: Optional[int] = None,
        currency: Optional[str] = None,
        fees: List[Fee] = [],
        **kwargs,
    ):
        self.broker = broker
        self.type = type
        self.quantity = quantity
        self.quantity_estimated = quantity_estimated
        self.price = price
        self.date = date
        self.order_id = order_id
        self.currency = currency
        self.fees = fees

        if kwargs:
            logging.debug(f"Received unexpected args: {kwargs}")


class Security(GeneralMethods):
    def __init__(
        self,
        isin: Optional[str] = None,
        _mongo_client: Optional["MongoClient"] = None,
        _ptf_id: Optional["ObjectId"] = None,
        **kwargs,
    ):
        self.isin = isin
        self.orders = []
        self._mongo_client: _mongo_client
        self._ptf_id: _ptf_id

        if kwargs:
            logging.debug(f"Received unexpected args for {self.ticker}: {kwargs}")

    def add_order(self, order: Order):
        self.orders.append(order)
        logging.debug(f"Order {order.order_id} added to '{self.ticker}' ({self.isin})")

    def push(self):
        security_dict = self.to_dict()
        category = self.class_to_cat(self)
        self._mongo_client.investments.portfolios.find_one_and_update(
            filter={"_id": self._ptf_id},
            update={"$push": {f"{category}.$[elem].orders": {"$each": security_dict}}},
            array_filters=[{"elem.isin": self.isin}],
        )


class Stock(Security):
    def __init__(
        self,
        ticker: Optional[str] = None,
        t212_id: Optional[str] = None,
        sector: Optional[str] = None,
        country: Optional[str] = None,
        **kwargs,
    ):
        self.ticker = ticker
        self.t212_id = t212_id
        self.sector = sector
        self.country = country
        super().__init__(**kwargs)


class Bond(Security):
    # WIP
    pass
