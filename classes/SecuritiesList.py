from dataclasses import dataclass, field
from securities import Stock, Bond, Security
import pandas as pd
import yfinance as yf

@dataclass
class SecuritiesList:
    security_type: Stock | Bond # Add more if needed
    positions: list[Security] = field(default_factory=list)
    stats: dict = field(default_factory=dict) # WIP

    def fetch_history_many(self, start_date: str, end_date: str, tickers: list | None = None):
        '''
        Fetch historical market data for multiple tickers within a specified date range.

        Parameters:
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.
        - tickers (list | None): List of ticker symbols to fetch data for. If None, fetches data for all tickers in self.positions.
        '''
        if tickers is not None:
            tickers = [security.ticker for security in self.positions if security.ticker != '']
        df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
        self._handle_fetch_history(df)
    
    def fetch_history(self): # WIP
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