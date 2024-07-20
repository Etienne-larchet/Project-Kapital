import logging
from typing import Literal, TYPE_CHECKING
from datetime import datetime

from .generals import GeneralMethods

if TYPE_CHECKING:
    from pymongo import MongoClient
    from bson import ObjectId


class Order():
    def __init__(self, broker: Literal['T212', 'IBKR', 'TR'] | None = None, type: Literal['LIMIT', 'MARKET'] | None = None, 
                 quantity: float | None = None, price: float | None = None, date: datetime | None = None, 
                 order_id: int | None = None, **kwargs):
        self.broker = broker
        self.type = type
        self.quantity = quantity
        self.price = price
        self.date = date
        self.order_id = order_id

        if kwargs: 
            logging.debug(f'Received unexpected args: {kwargs}')


class Security(GeneralMethods):
    def __init__(self, **kwargs):
        self.orders = []
        self._mongo_client: 'MongoClient | None' = kwargs.pop('_mongo_client', None)
        self._ptf_id: 'ObjectId | None' = kwargs.pop('_ptf_id', None)

        if kwargs:
            logging.debug(f'Received unexpected args for {self.ticker}: {kwargs}')
    
    def add_order(self, order: Order) -> Order:
        self.orders.append(order)
        if self._mongo_client:
            category = self.class_to_cat(self)
            self._mongo_client.investissements.portfolios.find_one_and_update(
                filter={'_id':self._ptf_id}, 
                update={ '$push':{f'{category}.{self.isin}.orders': order.__dict__}}, 
                upsert=True)
        logging.debug(f"Order {order.order_id} added to '{self.ticker}' ({self.isin})")
        return self.orders[-1]


class Stock(Security):
    def __init__(self, isin: str |None = None, ticker: str | None = None, t212_id: str | None = None, 
                 sector: str | None = None, country: str | None = None, **kwargs):
        self.ticker = ticker
        self.t212_id = t212_id
        self.isin = isin
        self.sector = sector
        self.country = country
        super().__init__(**kwargs)


class Bond(Security):
    # WIP
    pass