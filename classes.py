from dataclasses import dataclass, field, asdict
import pandas as pd
import yfinance as yf
import json


@dataclass(kw_only=True)
class Security:
    quantity: int
    risk: int | None = None
    variance: int | None = None
    sd: int | None = None
    history = pd.DataFrame({
         "date_str": [], 
         "date_ts": [],
         "open": [],
         "close": [],
         "adjusted": [],  
    })


@dataclass
class Stock(Security):
    ticker: str
    sector: str | None = None
    country: str | None = None

    def __init__(self, ticker: str, sector: str | None = None, country: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.ticker = ticker
        self.sector = sector
        self.country = country


@dataclass
class Bond(Security):
    # WIP
    pass


@dataclass
class SecuritiesList:
    security_type: Stock | Bond
    positions: list[Security] = field(default_factory=list)
    stats: dict = field(default_factory=dict) # WIP

    def mass_fetch_history(self, start_date: str, end_date: str):
        # Expected date format: 'YYYY-MM-DD'
        tickers = []
        for ticker in self.positions.keys():
            tickers.append(ticker)
        data = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
        return data
    
    def update(self):
        # WIP
        pass

    def from_dict(self, data):
        self.stats = data["stats"]
        positions = data["positions"]
        for pos in positions:
            self.positions.append(self.security_type(**pos))


@dataclass
class Portfolio:
    stocks: SecuritiesList = field(default_factory=lambda: SecuritiesList(Stock))
    bonds: SecuritiesList = field(default_factory=lambda: SecuritiesList(Bond))
    stats: dict = field(default_factory=dict)
    
    def add_security(self, type: int, ticker: str, quantity: int) -> None:
        match type:
            case 0: 
                    self.stocks.positions.append(Stock(ticker, quantity = quantity))
            case 1:
                pass # Use for bonds, WIP

    def export(self, file_path: str)-> None:
        with open(file_path, "w") as file:
            ex = asdict(self)
            del ex["bonds"]["security_type"], ex["stocks"]["security_type"]
            json.dump(ex, file, indent=4)
    
    def load(self, file_path: str) -> None:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise ValueError("File not found at path", file_path)
        except Exception as e:
            raise ValueError(f'Error: {e}')
        
        for attr, value in data.items():
            match attr:
                case "bonds":
                    self.bonds.from_dict(value)
                case "stocks":
                     self.stocks.from_dict(value)
                case "stats":
                    self.stats = value
        
        

def main() -> None:
    ptf = Portfolio()
    ptf.add_security(0,"22222", 23)
    ptf.load("./test.json")
    ptf.add_security(0, "12", 2)

    # ptf.stocks.update() -> WIP
    ptf.export("./test.json")
     

if __name__ == "__main__":
    main()
