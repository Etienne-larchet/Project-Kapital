from dataclasses import dataclass, field, asdict
from classes.Securities import Stock, Bond
import json
import sys
from typing import Literal
from classes.SecuritiesList import SecuritiesList


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