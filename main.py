from classes import Portfolio


ptf = Portfolio()
ptf.add_security(0, "msft")
print(ptf.stocks.positions)

