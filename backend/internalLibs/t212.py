import datetime as dt
import json
import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import requests

from .decorators import timing

if TYPE_CHECKING:
    from pymongo import MongoClient


logger = logging.getLogger("myapp")


@dataclass()
class Trading212:
    token: str
    mongo_client: "Optional[MongoClient]" = None

    def get_positions(self, t212_id: Optional[str] = None) -> json:
        url = "https://live.trading212.com/api/v0/equity/portfolio"
        if t212_id is not None:
            url += "/" + t212_id
        data = Trading212._handle_request(url=url, api_key=self.token)
        data = Trading212._change_semantic(data)
        return data

    @timing()
    def get_instruments(
        self, filter: Dict[str, Union[str, List[str]]], update: bool = False
    ) -> List[Dict[str, Any]]:
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

        query = {search_key: {"$in": search_values}}
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
                logger.info(
                    f"Values {missing_values} not found, updating instruments table."
                )
                self.update_instruments()
                for value in missing_values:
                    result = self.get_instruments({search_key: value}, update=False)
                    if result:
                        return_data.extend(result)
            else:
                for value in missing_values:
                    logger.warning(f"{value} does not exist.")

        return return_data

    @timing()
    def get_orders(
        self,
        from_date: Optional[datetime] = None,
        chunk_size: int = 50,
        filter_func: Optional[callable] = None,
    ) -> list:
        url = "https://live.trading212.com/api/v0/equity/history/orders"
        query = {
            "limit": chunk_size,
            "cursor": None,
        }
        page_nb = 0
        orders = []
        ids = (
            []
        )  # assumption that orders splitted in 2 are always fetch together during the same get_orders call
        looper = True

        logger.info(
            f"Starting get_orders with params from_date: {from_date}; chunk_size: {chunk_size}"
        )
        while looper:
            data = Trading212._handle_request(
                url=url, api_key=self.token, params=query, delay_btw_calls=4
            )
            items = data["items"]
            if not items:
                break

            page_nb += 1
            next_cursor_dt = datetime.strptime(
                items[-1]["dateModified"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )  # potentiels issues if 2 orders have the same date
            next_cursor_ts = int(next_cursor_dt.timestamp() * 1000)
            query["cursor"] = next_cursor_ts
            logger.info(
                f"Page {page_nb:03} - Next cursor at: {next_cursor_ts} - {datetime.fromtimestamp(next_cursor_ts/1000, dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}"
            )

            for order in items:
                if from_date:
                    date = datetime.strptime(
                        order["dateModified"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    if date < from_date:
                        looper = False
                        continue
                if filter_func and not filter_func(order):
                    continue
                if order["id"] not in ids:
                    orders.append(order)
                    ids.append(order["id"])
                else:
                    orders[-1]["taxes"].extend(
                        order["taxes"]
                    )  # potentiels issues if splitted orders are not following each others (which should not be the case)

        orders = self._change_semantic(orders)
        logger.info(f"Nb transactions fetched: {len(orders)}")
        return orders

    def get_open_orders(self, id: Optional[str] = None) -> json:
        """
        Fetch orders from the Trading212 API.

        **Parameters**
        id (str | None): Specific order ID to fetch. Fetches all orders if None.
        """
        url = "https://live.trading212.com/api/v0/equity/orders"
        if id is not None:
            url += "/" + id
        return Trading212._handle_request(url=url, api_key=self.token)

    def get_account_stats(self) -> json:
        url = "https://live.trading212.com/api/v0/equity/account/cash"
        return Trading212._handle_request(url, self.token)

    def update_instruments(self) -> list:
        url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
        data = Trading212._handle_request(url=url, api_key=self.token)

        # change semantic to avoid any confusion
        instruments = Trading212._change_semantic(data)

        if self.mongo_client is None:
            logger.info("Mongo client not connected, update not saved")
            return instruments

        # init mongo client
        instruments_pt = self.mongo_client.brokers.t212_instruments

        instruments_id = [ins["t212_id"] for ins in instruments]
        mongo_ins = instruments_pt.find({"t212_id": {"$in": instruments_id}})
        mong_ins_id = [ins["t212_id"] for ins in mongo_ins]
        new_ins = [
            instrument
            for instrument in instruments
            if instrument["t212_id"] not in mong_ins_id
        ]
        if new_ins:
            instruments_pt.insert_many(new_ins)
        return new_ins

    @staticmethod
    def _handle_request(
        url: str,
        api_key: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        delay_btw_calls: float = 2,
    ) -> json:
        full_headers = {"Authorization": api_key}
        if headers is not None:
            full_headers.update(headers)
        response = requests.get(url, headers=full_headers, params=params)
        match response.status_code:
            case 200:
                return response.json()
            case 429 | 520:
                time.sleep(delay_btw_calls)
                new = Trading212._handle_request(
                    url=url, api_key=api_key, headers=headers, params=params
                )
                return new
            case _:
                logger.error(
                    f"Error: {response.status_code} while fetching data: {response.json()}"
                )
                sys.exit()  # WIP

    @staticmethod
    def _change_semantic(
        data: list,
    ) -> list:  # Changement of semantic to avoid confusion in later operations
        for el in data:
            try:
                el["t212_id"] = el.pop("ticker")
                el["ticker"] = el.pop("shortName")
                del el["workingScheduleId"]
                del el["minTradeQuantity"]
                del el["maxOpenQuantity"]
                del el["addedOn"]
            except KeyError as e:
                # logger.debug(f"Fail to get key {e} for object {el.get("t212_id", el.get("ticker", None))}")
                continue
            except Exception as e:
                logger.error(e)
        return data
