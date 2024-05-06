from portfolio import Portfolio
import json


ptf = Portfolio()

with open('tickers_list.json', 'r') as file:
    data = json.load(file)

tickers = data['data']

for i in tickers:
    ptf.add_security("stock", i["yf_ticker"], t212_id = i['broker_ticker'])

ptf.export("Portfolio.json")
