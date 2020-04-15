import pandas as pd
from yahoo_fin import stock_info as si
import datetime
import pytz
import asyncio
import numpy as np
import time
import requests

# http://theautomatic.net/yahoo_fin-documentation/#get_day_most_active
# http://theautomatic.net/2018/07/31/how-to-get-live-stock-prices-with-python/
# https://stackoverflow.com/questions/11869910/pandas-filter-rows-of-dataframe-with-operator-chaining

# df = pd.DataFrame(columns=['symbol', 'price', 'time', 'volume', '% change'])
df = pd.DataFrame(columns=['pos', 'symbol', 'price', 'req_time', 'res_time'])
# df = pd.DataFrame(columns=['price', 'time'])
def get_most_active_tickers(ticker=''):
    r = (si.get_day_most_active()).sort_values(by='Volume', ascending=False)
    if not ticker:
        return (r[['Symbol', 'Price (Intraday)', '% Change', 'Volume' , 'Avg Vol (3 month)']]) 
    else:
        res= r[r.Symbol == ticker]
        # print (res[['Price (Intraday)', '% Change', 'Volume']])
        return res[['Price (Intraday)', '% Change', 'Volume']]
    # return r
    # return (r.sort_values(by=['Price (Intraday)'])[['Symbol', 'Symbol', 'Price (Intraday)', '% Change', 'Volume', 'Avg Vol (3 month)']]) 
    # print(r.sort_values(by=['Price (Intraday)'])[['Symbol', 'Symbol', 'Price (Intraday)', '% Change', 'Volume', 'Avg Vol (3 month)']])
# print(list(r))
# print(r[['Symbol', 'Symbol', 'Price (Intraday)', '% Change', 'Volume', 'Avg Vol (3 month)']])

# async def get_price(ticker):
#     base_url ='https://query1.finance.yahoo.com/v8/finance/chart/'
#     if end_date is None:  
#         end_seconds = int(time.time())
        
#     else:
#         end_seconds = int(pd.Timestamp(end_date).timestamp())
        
#     if start_date is None:
#         start_seconds = int(time.time())
        
#     else:
#         start_seconds = int(pd.Timestamp(start_date).timestamp())
#     # interval in : "1d", "1wk", "1mo"
#     interval = "1d"
#     params = {"period1": start_seconds, "period2": start_seconds, "interval" : "1d", "events": "div,splits"}
#     resp = requests.get(base_url + ticker, params = params)
#     if not resp.ok:
#         raise AssertionError(resp.json())
    

async def get_price(ticker, pos):
    now = datetime.datetime.now(pytz.utc)
    reqs =  
    price = si.get_live_price(ticker)
    now = datetime.datetime.now(pytz.utc)
    nows = (now.astimezone(pytz.timezone('US/Eastern'))).strftime("%H:%M:%S.%f")[:-3]
    # r= get_most_active_tickers(ticker)
    # print(ticker, "%.2f" % price, now.astimezone(pytz.timezone('US/Eastern')))
    # df.loc[pos] = [ticker, "%.2f" % price, (now.astimezone(pytz.timezone('US/Eastern'))).strftime("%H:%M:%S"), r.iloc[0]['Volume'], r.iloc[0]['% Change']]
    df.loc[str(pos) + ticker] = [pos, ticker, "%.2f" % price, reqs, (now.astimezone(pytz.timezone('US/Eastern'))).strftime("%H:%M:%S")]
    # print(pos, ticker, "%.2f" % price, (now.astimezone(pytz.timezone('US/Eastern'))).strftime("%H:%M:%S") )
    # return "%.2f" % price
    print (ticker, "%.2f" % price, reqs, nows)

def get_ticker_by_volume(tickers, price:int):
   below_cap_price = tickers['Price (Intraday)'] <= price
   volume = tickers['Volume'] >= 10000000
   vol_up = tickers['Volume'] < 1000000000
   r = tickers[below_cap_price & volume & vol_up].sort_values(by='Volume', ascending=False).head(50)
   # r = tickers[tickers['Price (Intraday)'] < 10].sort_values(by='Volume').tail(3)
#    print(r)
   return r

def get_high_change_ticker(tickers):
   positive_change = tickers['% Change'] > 0
   r = tickers[positive_change].sort_values(by='% Change', ascending=False).head(20)
   # r = r[r['Price (Intraday)'] < 50].sort_values(by='% Change').tail(3)
#    print(r)
   return r

async def get_tickers(price:int):
    r = get_most_active_tickers()
    r = get_ticker_by_volume(r, price)
    r = get_high_change_ticker(r)
    return r

def main():
    i = 0
    prev_price =0
    # prev_price2 = 0
    while (True):
        prev_price = asyncio.run(get_price('PBR', i, prev_price))
        i=i+1
        # prev_price2 = asyncio.run(get_price('MRO', i, prev_price2))
        # i=i+1
        
        # if i % 10 == 0:
        #     print(df) 
            # break
        # else:
        print(df.mean())
        time.sleep(1)

if __name__ == "__main__":
    main()
# main()
# r = si.get_quote_table('ET')
# print(r)