import logging
from datetime import datetime, timezone
from time import time

from mylibs.t212 import Trading212
from master.mongodb import mongo_client
from classes.securities import Order, Stock
from classes.portfolio import Portfolio
from classes.users import User

logging.basicConfig(level=logging.INFO)


def updateT212(client_id):
    # Initialization
    user = User(client_id, mongo_client=mongo_client)
    user.connect_user(fast_connect=True)
    ptf = Portfolio(mongo_client, user.ptf_ids[0] if user.ptf_ids else None) # ptf[0] is always the 'basket ptf'
    if not user.ptf_ids:
        user.add_ptf_id(ptf._id)
    t = time()
    ptf.load()
    logging.info(f"Portfolio loading time: {time() - t}")
    t212 = Trading212(user.oaths['T212'], mongo_client)

    # Getting orders from a specific date
    last_date = user.brokersLastUpdate.get('T212', None)
    t = time()
    orders = t212.get_orders(last_date)
    logging.info(f'Fetching orders time: {time() - t}')

    # Creating a dictionary of old stocks
    existing_stocks = {stock.t212_id: stock for stock in ptf.stocks.values()}
    existing_t212_ids = set(existing_stocks.keys())
    filtered_orders = []
    new_t212_ids = []

    # Filtering orders and identifying new t212_ids
    for order in orders:
        if order['status'] == 'FILLED':
            t212_id = order['t212_id']
            if t212_id not in existing_t212_ids and t212_id not in new_t212_ids:
                new_t212_ids.append(t212_id) # progress to do for users with multiple portfolios
            filtered_orders.append(order)

    orders = filtered_orders
    
    # Fetching instruments for new t212_ids
    t = time()
    instruments = t212.get_instruments({'t212_id': new_t212_ids})
    logging.info(f'Instruments list fetched in {time() - t}')

    instruments_dict = {instrument['t212_id']: instrument for instrument in instruments}

    # Processing each order
    t = time()
    for order in orders:
        t212_id = order['t212_id']
        order_dict = {
            'broker': 'T212',
            'type': order['type'],
            'quantity': order['filledValue'] if order['filledValue'] is not None else order['filledQuantity'],
            'price': order['fillPrice'],
            'date': datetime.strptime(order['dateModified'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            'order_id': order['id'],
        }
        order_obj = Order(**order_dict)

        stock: Stock = existing_stocks.get(t212_id)
        if stock:
            stock.add_order(order_obj)
        else:
            instrument = instruments_dict.get(t212_id)
            if instrument:
                stock_dict = {
                    'isin': instrument['isin'],
                    'ticker': instrument['ticker'],
                    't212_id': t212_id,
                }
                stock_obj = Stock(**stock_dict)
                stock_obj.add_order(order_obj)
                added_stock = ptf.add(stock_obj)
                existing_stocks[t212_id] = added_stock
            else:
                logging.warning(f"Instrument for t212_id: '{t212_id}' not found.")
    logging.info(f'Orders update time: {time() -t}')

    t = time()
    user._users_db.users.update_one(
        {'_id': user._id},
        {'$set': {'brokersLastUpdate.T212': datetime.now(timezone.utc)}})
    logging.info(f'T212 update date added to mongo in: {time() -t}')
    return orders