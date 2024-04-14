from classes import Portfolio
from Oath import ApiKeys
import requests
import sys

def get_broker_portfolio(url, headers) -> list:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} while fetching data")
        sys.exit()
    
    
def main() -> None:
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    headers = {"Authorization": ApiKeys.t212}
    print("Fetching portfolio positions from broker...")
    data = get_broker_portfolio(url, headers)

    ptf = Portfolio()
    for i in data:
        ticker = i['ticker'].split("_")[0]
        ptf.add_security(0, ticker, i['quantity'])
    print(ptf.stocks.positions)
    

if __name__ == "__main__":
    main()