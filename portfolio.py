from dataclasses import dataclass, field, asdict
from securities import Stock, Bond, Security
import pandas as pd
import yfinance as yf
import json
import sys
from typing import Literal


@dataclass
class SecuritiesList:
    security_type: Stock | Bond # Add more if needed
    positions: list[Security] = field(default_factory=list)
    stats: dict = field(default_factory=dict) # WIP

    def fetch_history_many(self, start_date: str, end_date: str):
        # Expected date format: 'YYYY-MM-DD'
        tickers = [security.ticker for security in self.positions if security.ticker != ''] # Update to be able to select which tickers to use, default is all.
        df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
        self._handle_fetch_history(df)
    
    def fetch_history(): # WIP
        pass

    def _handle_fetch_history(self, df: pd.DataFrame)-> None:
        df_list = [(ticker, df[ticker]) for ticker in df.columns.levels[0]]
        for ticker, df in df_list:
            df.index = df.index.strftime('%d/%m/%Y') # Convert Datetime object to str // .astype('int64') for ts format
            df = df.dropna(axis='index', how='all')
            history = df.to_dict(orient="index")
            self.update(ticker, {'history': history})
    
    def update(self, ticker: str, update_security: dict, upsert: bool = False) -> tuple:
        for el in self.positions:
            if ticker == el.ticker:
                for key, value in update_security.items():
                    if isinstance(value, dict): # progess to do, for now only one level dict is allowed => transform it to recursive function to handle more layers
                        for col, col_value in value.items():
                            el[key][col] = col_value
                    else:
                        el[key] = value
                return 1, f"Security'{ticker}' updated"
        if upsert == True:
            update_security["ticker"] = ticker
            self.add(update_security)
            return 2, f"Security '{ticker}' added"
        return 0, f"Security '{ticker}' not found"

    def add(self, security: Security) -> None:
            self.positions.append(self.security_type(**security))

    def from_dict(self, data) -> None:
        self.stats = data["stats"]
        positions = data["positions"]
        for pos in positions:
            self.positions.append(self.security_type(**pos))

    def get(self, ticker: str):
        for security in self.positions:
            if ticker == security.ticker:
                return security
        return 0, "Security not found"


@dataclass
class Portfolio:
    stocks: SecuritiesList = field(default_factory=lambda: SecuritiesList(Stock))
    bonds: SecuritiesList = field(default_factory=lambda: SecuritiesList(Bond))
    stats: dict = field(default_factory=dict)
    
    def add_security(self, type: Literal['stock', 'bond'], ticker: str, **kwargs) -> None:
        match type:
            case "stock": 
                    self.stocks.positions.append(Stock(ticker, **kwargs))
            case "bond":
                pass # Use for bonds, WIP

    def export(self, file_path: str)-> None:
        try:
            with open(file_path, "w") as file:
                ex = asdict(self)
                del ex["bonds"]["security_type"], ex["stocks"]["security_type"]
                json.dump(ex, file, indent=4, skipkeys=True)
        except Exception as e:
            print("Error while saving:", e)
            print('data:', file)
            sys.exit()
    
    def load(self, file_path: str) -> int:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"File not found at path: {file_path}")
            return 0
        except Exception as e:
            print(f'Error: {e}')
            sys.exit()
        for attr, value in data.items():
            match attr:
                case "bonds":
                    self.bonds.from_dict(value)
                case "stocks":
                     self.stocks.from_dict(value)
                case "stats":
                    self.stats = value
        return 1