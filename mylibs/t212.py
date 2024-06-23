import requests
import json
import sys
import time
from dataclasses import dataclass
import inspect
import logging
from typing import List, Dict, Any
from os.path import join


@dataclass
class Trading212:
    api_key: str # Further improvement to accept a cryptographic key/file
    root_path: str = "DB-T212/"
    instruments_path: str = join(root_path, "instruments.json")
    transactions_path: str = join(root_path, "transactions.json")
       
    def get_orders(self, id: str | None = None) -> json:
        '''
        Fetch orders from the Trading212 API.

        **Parameters**
        id (str | None): Specific order ID to fetch. Fetches all orders if None.
        '''
        url = 'https://live.trading212.com/api/v0/equity/orders'
        if id is not None:
            url += "/" + id
        return Trading212._handle_request(url=url, api_key=self.api_key)

    def get_positions(self, t212_id: str | None = None) -> json:
        url = "https://live.trading212.com/api/v0/equity/portfolio"
        if t212_id is not None:
            url += "/" + t212_id
        data = Trading212._handle_request(url=url, api_key=self.api_key)
        data = Trading212._change_semantic(data)
        return data
    
    def get_instruments(self, instruments_path: str = None, update: bool = False) -> json:
        if instruments_path is None:
            instruments_path = self.instruments_path
        if update:
            return self.update_instruments()
        else:
            try:
                with open(instruments_path, 'r') as file:
                    data = json.load(file)
            except Exception as e:
                print('Error while accessing file:', e)
            return data
        
    def search_instruments(self, filter: Dict[str, str | List[str]], update: bool = True) -> List[Dict[str, Any]]:
        """
        Search for instruments based on a filter.

        Args:
            filter (dict): The filter to apply. For example:
                {'t212_id': 'AAPL_US_EQ'},
                {'ticker': 'AAPL'},
                {'ticker': ['AAPL', 'MSFT', 'TSLA']}
            update (bool): Whether to update instruments if a value is not found. Defaults to True.
        """       
        search_key = next(iter(filter))
        search_values = filter[search_key]
        
        if not isinstance(search_values, list):
            search_values = [search_values]
        
        return_data = []
        instruments_list = self.get_instruments()
        
        for value in search_values:
            found = False
            for instrument in instruments_list:
                if instrument.get(search_key) == value:
                    return_data.append(instrument)
                    found = True
                    break
            
            if not found:
                if not update:
                    logging.warning(f'{value} does not exist.')
                else:           
                    logging.info(f'{value} not found, updating instruments table.')
                    instruments_list = self.update_instruments()
                    update = False  # Avoid multiple updates in a single search
                    
                    result = self.search_instruments({search_key: value}, update=update)
                    if result:
                        return_data.extend(result)
            
        return return_data
        
    def get_transactions(self, update: bool = False) -> list:
        base1 = "https://live.trading212.com/"
        base2 = "api/v0/equity/history/orders"
        query = {
        "limit": 50,
        }
        page_nb = 1
        orders = []
        while True:
            data = Trading212._handle_request(url=base1+base2, api_key=self.api_key, params=query)
            base2 = data['nextPagePath']
            orders += data['items']
            print('Page', page_nb)
            page_nb += 1
            if base2 is None:
                break
        print('Nb transactions:', len(orders))
        a = time.time()
        for order in orders:
                keys_to_remove = [key for key, value in order.items() if value is None]
                for key in keys_to_remove:
                    del order[key]
        print("Fitering time:", time.time()-a)
        if not update:
            return orders
        else:
            with open(self.transactions_path, "w") as file:
                json.dump(orders, file, indent=4)
        
    def get_account_stats(self) ->json:
        url = "https://live.trading212.com/api/v0/equity/account/cash"
        return Trading212._handle_request(url, self.api_key)

    def update_instruments(self) -> json:       
        url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
        data = Trading212._handle_request(url=url, api_key=self.api_key)

        # change of semantic to avoid any confusion
        data = Trading212._change_semantic(data)

        with open(self.instruments_path, "w") as file:
            json.dump(data, file, indent=4)
        return data
    
    def search(self, data: list, compare_el: str,  method, method_args: list = None, update: bool = False): #WIP
        for el in data:
            if el.get(compare_el, None) is None:
                print('Key not found')
            results = method(update=update, **method_args)
            for result in results:
                if result.get(compare_el, None) is None:
                    print('key not found in method return')
                    if update is True:
                        params = inspect.signature(method).parameters # check if given function received 'update'params
                        # if 'update' in params:
           
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
                time.sleep(3)
                new = Trading212._handle_request(url=url, api_key=api_key, headers=headers, params=params)
                return new
            case _:
                logging.error(f"Error: {response.status_code} while fetching data")
                sys.exit()
    
    @staticmethod
    def _change_semantic(data: list) -> list: # Changement of semantic to avoid confusion in later operations
        for el in data:
            try:
                el['t212_id'] = el.pop('ticker')
                el['ticker'] = el.pop('shortName')
            except KeyError as e:
                logging.info(f"Fail to get key {e} for object {el.get("t212_id", el.get("ticker", None))}")
                continue
            except Exception as e:
                logging.error(e)
        return data