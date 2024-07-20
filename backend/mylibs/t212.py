import requests
import json
import sys
import time
import logging
from dataclasses import dataclass
from typing import Union, Dict, List, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from pymongo import MongoClient


@dataclass()
class Trading212:
    t212_key: str
    mongo_client: 'MongoClient | None' = None
       
    def get_positions(self, t212_id: str | None = None) -> json:
        url = "https://live.trading212.com/api/v0/equity/portfolio"
        if t212_id is not None:
            url += "/" + t212_id
        data = Trading212._handle_request(url=url, api_key=self.t212_key)
        data = Trading212._change_semantic(data)
        return data

    def get_instruments(self, filter: Dict[str, Union[str, List[str]]], update: bool = False) -> List[Dict[str, Any]]:
        """
        Search for instruments based on a filter.

        Args:
            filter (dict): The filter to apply. For example:
                {'t212_id': 'AAPL_US_EQ'},
                {'ticker': 'AAPL'},
                {'ticker': ['AAPL', 'MSFT', 'TSLA']}
            update (bool): Whether to update instruments if a value is not found. Defaults to False.
        """
        search_key = next(iter(filter))
        search_values = filter[search_key]

        if not isinstance(search_values, list):
            search_values = [search_values]

        query = {search_key: {'$in': search_values}}
        instruments = list(self.mongo_client.brokers.t212_instruments.find(query))
        return_data = []
        missing_values = []

        for value in search_values:
            found = False
            for instrument in instruments:
                if instrument.get(search_key) == value:
                    return_data.append(instrument)
                    found = True
            if not found:
                missing_values.append(value)
        if missing_values:
            if update:
                logging.info(f'Values {missing_values} not found, updating instruments table.')
                self.update_instruments()
                for value in missing_values:
                    result = self.get_instruments({search_key: value}, update=False)
                    if result:
                        return_data.extend(result)
            else:
                for value in missing_values:
                    logging.warning(f'{value} does not exist.')

        return return_data    
        
    def get_orders(self, from_date: datetime | None = None, chunk_size: int = 50) -> list:
        base1 = "https://live.trading212.com/"
        base2 = "api/v0/equity/history/orders"
        query = {
        "limit": chunk_size,
        }
        page_nb = 0
        orders = []
        looper = True

        while looper:
            data = Trading212._handle_request(url=base1+base2, api_key=self.t212_key, params=query)
            base2 = data['nextPagePath']
            items = data['items']
            orders += items
            page_nb += 1
            logging.info(f'Page {page_nb}')
            
            if from_date:
                for order in items[::-1]: # Issues in latter operations may arise for none-executed orders that may be modified
                    date = datetime.strptime(order['dateCreated'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if date < from_date:
                        del orders[-1]
                        looper = False
                    else:
                        break

            if base2 is None:
                break

        orders = self._change_semantic(orders)
        logging.info(f'Nb transactions fetched: {len(orders)}')
        return orders
    
    def get_open_orders(self, id: str | None = None) -> json:
        '''
        Fetch orders from the Trading212 API.

        **Parameters**
        id (str | None): Specific order ID to fetch. Fetches all orders if None.
        '''
        url = 'https://live.trading212.com/api/v0/equity/orders'
        if id is not None:
            url += "/" + id
        return Trading212._handle_request(url=url, api_key=self.t212_key) 
        
    def get_account_stats(self) ->json:
        url = "https://live.trading212.com/api/v0/equity/account/cash"
        return Trading212._handle_request(url, self.t212_key)

    def update_instruments(self) -> list:      
        url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
        data = Trading212._handle_request(url=url, api_key=self.t212_key)

        # change semantic to avoid any confusion
        instruments = Trading212._change_semantic(data)

        if self.mongo_client is None:
            logging.info('Mongo client not connected, update not saved')
            return instruments
        
        # init mongo client
        instruments_pt = self.mongo_client.brokers.t212_instruments

        instruments_id = [ins['t212_id'] for ins in instruments]
        mongo_ins = instruments_pt.find({'t212_id': {'$in': instruments_id}})
        mong_ins_id = [ins['t212_id'] for ins in mongo_ins]
        new_ins = [instrument for instrument in instruments if instrument['t212_id'] not in mong_ins_id]
        if new_ins:
            instruments_pt.insert_many(new_ins)
        return new_ins
           
    @staticmethod
    def _handle_request(url: str, api_key: str, headers: dict = None, params: dict = None) -> json:
        full_headers = {"Authorization": api_key}
        if headers is not None:
            full_headers.update(headers)
        response = requests.get(url, headers=full_headers, params=params)
        match response.status_code:
            case 200:
                return response.json()
            case 429:
                time.sleep(1.5)
                new = Trading212._handle_request(url=url, api_key=api_key, headers=headers, params=params)
                return new
            case _:
                logging.error(f"Error: {response.status_code} while fetching data")
                sys.exit()
    
    @staticmethod
    def _change_semantic(data: list) -> list: # Changement of semantic to avoid confusion in latter operations
        for el in data:
            try:
                el['t212_id'] = el.pop('ticker')
                el['ticker'] = el.pop('shortName')
                del el['workingScheduleId']
                del el['minTradeQuantity']
                del el['maxOpenQuantity']
                del el['addedOn']
            except KeyError as e:
                logging.debug(f"Fail to get key {e} for object {el.get("t212_id", el.get("ticker", None))}")
                continue
            except Exception as e:
                logging.error(e)
        return data