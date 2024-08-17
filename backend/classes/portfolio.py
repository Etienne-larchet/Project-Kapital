import logging
from datetime import datetime
from typing import TYPE_CHECKING, List, Literal, Optional, Union

from bson.objectid import ObjectId
from fxrates import ExchangeRate

from internalLibs.decorators import timing

from .generals import GeneralMethods
from .securities import Bond, Fee, Order, Stock

if TYPE_CHECKING:
    from pymongo import MongoClient


class Portfolio(GeneralMethods):
    def __init__(
        self,
        mongo_client: Optional["MongoClient"] = None,
        ptf_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self._mongo_client = mongo_client
        self._id = ObjectId(ptf_id)
        self.stocks = []
        self.bonds = []
        self.name = name

    @timing()
    def load(self, ptf_id: str | Optional[ObjectId] = None):
        if ptf_id:
            self._id = ObjectId(ptf_id)
        ptf = self._mongo_client.investments.portfolios.find_one({"_id": self._id})
        if ptf:
            self.from_dict(self, ptf, classes=[Portfolio, Stock, Bond, Order, Fee])
        else:
            logging.info(f"No portfolio found with id '{self._id}'")

    def add_security(self, security: Union[Bond, Stock]) -> Union[Bond, Stock]:
        security._mongo_client = self._mongo_client
        security._ptf_id = self._id
        security_type = self.class_to_cat(security)
        getattr(self, security_type).append(security)
        return getattr(self, security_type)[-1]

    def push_securities(self, security_type: Literal["bonds", "stocks"]):
        securities_list = self.to_dict(getattr(self, security_type))
        self._mongo_client.investments.portfolios.find_one_and_update(
            filter={"_id": self._id},
            update={"$push": {security_type: {"$each": securities_list}}},
            upsert=True,
        )

    def stock_history(
        self,
        date_from: str,
        date_to: str,
        interval: Literal["d", "w", "m", "y"],
        currency: str = "EUR",
    ):
        result = {}
        for stock in self.stocks:
            for order in stock.orders:
                value = getattr(order, "quantity") * getattr(order, "price")
                order_currency = getattr(order, "currency")
                if order_currency != currency:
                    rate = ExchangeRate.convert(
                        target_codes=order_currency, base_code=currency, amount=value
                    )
                    value = list(rate["rates"].values())[0]
                date = datetime.strftime(getattr(order, "date"), "%Y-%m-%d")
                try:
                    result[date] += value
                except KeyError:
                    result[date] = value
        return {key: result[key] for key in sorted(result.keys())}

    def import_json(self, path: str):
        pass

    def export_json(self, path: str):  # WIP
        pass
