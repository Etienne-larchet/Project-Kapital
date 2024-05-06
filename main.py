import pandas as pd
import requests
import sys
import numpy as np

from portfolio import Portfolio
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

def fetch_broker() -> dict:
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    headers = {"Authorization": ApiKeys.t212}
    print("Fetching portfolio positions from broker.")
    data = get_broker_portfolio(url, headers)
    return data

def define_new_tickers(ptf: Portfolio, broker_data: dict) -> list:
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

    return update

def generate_random_weights(stocks):
    # Generate random weights
    weights = np.random.rand(len(stocks))
    # Normalize weights to sum up to 1
    weights /= np.sum(weights)
    return weights

    
def main() -> None:
    # Create Portfolio instance
    ptf = Portfolio()
    ptf.load("Portfolio.json")
    # # Fetch broker positions
    # broker_data = fetch_broker()
    # # Select new tickers and create/ update stock instances within the portfolio
    # update = define_new_tickers(ptf, broker_data)
    # for el in update:
    #     ptf.stocks.update(el[0], el[1], upsert=True)

    # Fetch prices history for each stock of the portfolio
    # ptf.stocks.fetch_history_many("2021-01-01", "2023-12-31")

    # Load portfolio data in a datafame
    stocks = ptf.stocks.positions
    ptf_data = {}
    for stock in stocks:
        df = pd.DataFrame(stock.history).transpose()
        log_return = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
        ptf_data[stock.ticker] = log_return
    
    tickers = ptf_data.keys()
    stocks_log_return = pd.concat(ptf_data.values(), keys=tickers, axis=1).dropna(axis='index')

    # Determine the X number of randoms weights
    stocks_weights = []
    for _ in range(10000):
        weight = generate_random_weights(tickers)
        stocks_weights.append(weight)
    weights = pd.DataFrame(stocks_weights, columns=tickers)

    # Calculate portfolio variance
    ptf_variances = []
    for _, row in weights.iterrows():
        ptf_variance = np.dot(np.dot(row, stocks_log_return.cov()), row.T)
        ptf_variances.append(ptf_variance)
    ptf_variances = np.array(ptf_variances)

    # Calculate portfolio standard deviation
    ptf_sd = np.sqrt(ptf_variances)

    # Calculate portfolio returns
    stocks_annualized_returns = ((1+stocks_log_return.mean()) ** 252 ) -1
    ptf_returns = np.dot(weights, stocks_annualized_returns)
    # print(ptf_returns)

    # Calculate the sharpe ratio
    sharpe_ratios = ptf_sd / ptf_returns
    # print(sharpe_ratios)

    # Concatenate all data for csv conversion
    expert1 = {
        'sharpe ratio': sharpe_ratios, 
        'Expected return': ptf_returns, 
        'standart Deviation': ptf_sd
    }
    a = pd.DataFrame(expert1)
    print(a)
    export = pd.concat([a, weights], axis=0)
    print(export)
    ptf.export("Portfolio.json")




if __name__ == "__main__":
    main()