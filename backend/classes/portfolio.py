import logging
from bson.objectid import ObjectId
from typing import Union, TYPE_CHECKING, Optional

from .securities import Stock, Bond, Order
from .generals import GeneralMethods

if TYPE_CHECKING:
    from pymongo import MongoClient


class Portfolio(GeneralMethods):
    def __init__(self, mongo_client: Optional['MongoClient'] = None, ptf_id: Optional[str] = None, name: Optional[str] = None ):
        self._mongo_client = mongo_client
        self._id = ObjectId(ptf_id)
        self.stocks = {}
        self.bonds = {}
        self.name = name
   
    def load(self, ptf_id: str | ObjectId | None = None):
        if ptf_id:
            self._id = ObjectId(ptf_id)
        ptf = self._mongo_client.investments.portfolios.find_one({'_id': self._id})
        if ptf:
            self.from_dict(self, ptf, classes=[Portfolio, Stock, Bond, Order])
        else:
            logging.info(f"No portfolio found with id '{self._id}'")

    def add(self, security: Union[Bond, Stock]) -> Union[Bond, Stock]:
        security._mongo_client = self._mongo_client
        security._ptf_id = self._id
        security_type = self.class_to_cat(security)
        getattr(self, security_type)[security.isin] = security

        if self._mongo_client:
            security_dict = security.to_dict()
            self._mongo_client.investments.portfolios.find_one_and_update(
                filter= {'_id': self._id},
                update= {'$set': {f'{security_type}.{security.isin}': security_dict}}, 
                upsert= True)
        logging.debug(f"Security '{security.ticker}' ({security.isin}) added to portfolio")
        return getattr(self, security_type)[security.isin]

    def import_json(self, path: str): # WIP
        pass

    def export_json(self, path: str): # WIP
        pass