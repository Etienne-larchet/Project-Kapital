import requests
import json
import sys
from dataclasses import dataclass
import time


@dataclass
class Trading212:
    api_key: str
    path: str = "DB/T212/"

    def update_tickers_list(self):       
        url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
        data = Trading212._handle_request(url=url, api_key=self.api_key)
    
        with open(self.path+"full_tickers_list.json", "w") as file:
            json.dump(data, file, indent=4)
        return data
       
    def get_orders(self, id: str | None = None):
        '''
        Fetch orders from the Trading212 API.

        **Parameters**
        id (str | None): Specific order ID to fetch. Fetches all orders if None.
        '''
        url = 'https://live.trading212.com/api/v0/equity/orders/'
        if id is not None:
            url += id
        return Trading212._handle_request(url=url, api_key=self.api_key)

    def get_positions(self, t212_id: str | None = None):
        url = "https://live.trading212.com/api/v0/equity/portfolio/"
        if t212_id is not None:
            url += t212_id
        return Trading212._handle_request(url=url, api_key=self.api_key)
    
    def get_tickers_list(self, path: str = None, update: bool = False):
        if path is None:
            path = self.tickers_list_path
        if not update:
            return self.update_tickers_list()
        else:
            try:
                with open(path, 'r') as file:
                    data = json.load(file)
            except Exception as e:
                print('Error while accessing file:', e)
            return data
        
    def get_transactions(self, update: bool = False):
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
            with open(self.path+"transactions.json", "w") as file:
                json.dump(orders, file, indent=4)

        
    def get_account_stats(self):
        url = "https://live.trading212.com/api/v0/equity/account/cash"
        return Trading212._handle_request(url, self.api_key)

           
    @staticmethod
    def _handle_request(url: str, api_key: str, headers: dict = None, params: dict = None):
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
                print(f"Error: {response.status_code} while fetching data")
                sys.exit()