from dataclasses import dataclass, field, asdict
import pandas as pd
import yfinance as yf
import json
import sys


@dataclass(kw_only=True)
class Security:
    quantity: int | None = None
    risk: int | None = None
    variance: int | None = None
    sd: int | None = None
    history: dict = field(default_factory=dict)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value) -> None:
        setattr(self, key, value)


@dataclass
class Stock(Security):
    ticker: str
    sector: str | None = None
    country: str | None = None
    t212_id: str | None = None

    def __init__(self, ticker: str, sector: str | None = None, country: str | None = None, t212_id: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.ticker = ticker
        self.sector = sector
        self.country = country
        self.t212_id = t212_id       


@dataclass
class Bond(Security):
    # WIP
    pass


@dataclass
class SecuritiesList:
    security_type: Stock | Bond # Add more if needed
    positions: list[Security] = field(default_factory=list)
    stats: dict = field(default_factory=dict) # WIP

    def fetch_history_many(self, start_date: str, end_date: str):
        # Expected date format: 'YYYY-MM-DD'
        tickers = [] # Update to be able to select which tickers to use, default is all.
        for security in self.positions:
            tickers.append(security.ticker)
        tickers.remove('')
        df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
        self._handle_fetch_history(df)
    
    def fetch_history(): # WIP
        pass

    def _handle_fetch_history(self, df: pd.DataFrame)-> None:
        tickers = df.columns.levels[0]
        df_list = [(ticker, df[ticker]) for ticker in tickers]
        for ticker, df in df_list:
            df.index = df.index.astype('int64') # Convert Datetime object to timestamp int
            history = df.to_dict(orient="index")
            print(ticker)
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
    
    def add_security(self, type: int, ticker: str, quantity: int) -> None:
        match type:
            case 0: 
                    self.stocks.positions.append(Stock(ticker, quantity = quantity))
            case 1:
                pass # Use for bonds, WIP

    def export(self, file_path: str)-> None:
        try:
            with open(file_path, "w") as file:
                ex = asdict(self)
                del ex["bonds"]["security_type"], ex["stocks"]["security_type"]
                json.dump(ex, file, indent=4)
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
        
        

def main() -> None:
    ptf = Portfolio()
    ptf.load("Portfolio.json")
    ptf.add_security(0, "ticker_test100", 100)
    ptf.export("Portfolio.json")
     

if __name__ == "__main__":
    main()
