import requests, json
import asyncio

KEY='PKGJRTELONNVXBD8LTWG'
SECRET='Ex5QqISOeU2qJUug/i7FEoZILoacKDLiQac0k0dT'
BASE_URL ='https://paper-api.alpaca.markets'


HEADERS = {'APCA-API-KEY-ID': KEY, 'APCA-API-SECRET-KEY': SECRET}

async def get_account() -> json:
    url = '{0}/v2/account'.format(BASE_URL)
    r = requests.get(url, headers=HEADERS)
    # print(json.loads(r.content))
    return json.loads(r.content)

# def add_watchlist(name, symbol):
#     url = '{0}/v2/watchlists'.format(BASE_URL)
#     r = requests.postget(url, headers=HEADERS)
#     print(json.loads(r.content))
#     return json.loads(r.content)

async def get_orders() -> json:
    url = '{0}/v2/orders'.format(BASE_URL)
    r = requests.get(url, headers=HEADERS)
    # print(json.loads(r.content))
    return json.loads(r.content)

def post_orders(symbol, qty:int, action, type, time_in_force) -> json:
    data = {
        "symbol" : symbol,
        "qty" : qty,
        "side" : action,
        "type"  : type,
        "time_in_force" : time_in_force
    }
    url = '{0}/v2/orders'.format(BASE_URL)
    r = requests.post(url, json=data, headers=HEADERS)
    # print(r.content)
    return json.loads(r.content)

def cancel_orders(order_id) -> bool:
    if order_id:
        url = '{0}/v2/orders/{1}'.format(BASE_URL, order_id)
        r = requests.delete(url, headers=HEADERS)
    else:
        url = '{0}/v2/orders'.format(BASE_URL)
        r = requests.delete(url, headers=HEADERS)
    if r.status_code == 404:
        print('Order Not Found')
        return False
    elif r.status_code == 422:
        print('Order Cannot be Cancelled')
        return False
    else:
        return True

async def get_order(order_id)-> json:
    url = '{0}/v2/orders/{1}'.format(BASE_URL, order_id)
    r = requests.get(url, headers=HEADERS)
    return json.loads(r.content)
    
async def get_positions(ticker=''):
    if ticker:
        url = '{0}/v2/positions/{1}'.format(BASE_URL, ticker)
        r = requests.get(url, headers=HEADERS)
        return json.loads(r.content)
    else:
        url = '{0}/v2/positions'.format(BASE_URL)
        r = requests.get(url, headers=HEADERS)
        return json.loads(r.content)


def get_my_buying_power():
    return 10

def get_my_selling_power():
    return 20

def get_transaction_status():
    return 10

if __name__ == "__main__":
    get_account()

# order = "{'symbol':'F', 'qty': '100', 'side':'buy', 'type': 'limit'}"
# post_orders('F', 100, 'buy', 'limit', 'market')
# get_orders()