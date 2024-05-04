import pandas as pd
import requests
import sys

from classes import Portfolio
from Oath import ApiKeys


def get_broker_portfolio(url, headers) -> list:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code} while fetching data")
        sys.exit()
    return response.json()

def get_ticker(stocks_list: dict) -> dict:
    data = {
        't212_id': [],
        'ticker': [],
        'quantity': []
    }
    df = pd.DataFrame(data)
    for index, stock in enumerate(stocks_list):
        ticker = input(f'{index+1}/{len(stocks_list)} - Yfinance ticker for {stock['ticker']} : ')
        new_row = {'t212_id': stock['ticker'], 'ticker': ticker, 'quantity': stock['quantity']}
        df.loc[len(df)] = new_row
        df = df.reset_index(drop=True)
    data = df.to_dict(orient="records")
    return data

    
def main() -> None:
    # Create Portfolio instance
    ptf = Portfolio()
    ptf.load("Portfolio.json")

    # Fetch broker positions
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    headers = {"Authorization": ApiKeys.t212}
    print("Fetching portfolio positions from broker.")
    broker_data = get_broker_portfolio(url, headers)

    # Select new tickers
    ptf_tickers = [(i['t212_id'], i['ticker']) for i in ptf.stocks.positions]
    new_stocks = [i for i in broker_data if i['ticker'] not in [t212_id for (t212_id, _) in ptf_tickers]]
    old_stocks = [i for i in broker_data if i not in new_stocks]

    update = []

    # New Stocks
    for index, stock in enumerate(new_stocks):
        ticker = input(f'{index+1}/{len(new_stocks)} - Yfinance ticker for {stock['ticker']} : ')
        update.append([ticker, {'t212_id': stock['ticker'], 'quantity': stock['quantity']}])

    # Old Stocks 
    for stock in old_stocks:
        ticker = ""
        for i in ptf_tickers:
            if stock['ticker'] == i[0]:
                ticker = i[1]
        update.append([ticker, {'quantity': stock['quantity']}]) 
    
    for el in update:
        ptf.stocks.update(el[0], el[1], upsert=True)

    ptf.stocks.fetch_history_many("2023-01-01", "2023-10-02")
    ptf.export("Portfolio.json")


if __name__ == "__main__":
    main()