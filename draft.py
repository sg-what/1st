# import transaction as tx
# import yfinance as yf
# from yfinance import stock_info

# yf.get_day_most_active()
# msft = yf.Ticker("AAPL")

# hist = msft.history(period="1d", interval="1m")
# # print(hist)
# data = hist.between_time("10:01:10", "11:02:12")
# print(data[['Volume', 'Open']])
# # print(data)

# def main():
#     b_power = tx.get_my_buying_power()
import asyncio

import most_active
import transaction
r = most_active.get_most_active_tickers()
# print(r.sort_values(by='% Change').tail(3))
# print(r.head(4))

# Symbol Price (Intraday)  Change  % Change      Volume  Avg Vol (3 month)  Market Cap  PE Ratio (TTM)

def get_ticker_by_volume(tickers, price:int):
   below_cap_price = tickers['Price (Intraday)'] <= price
   volume = tickers['Volume'] >= 1000000
   vol_up = tickers['Volume'] < 1000000000
   r = tickers[below_cap_price & volume & vol_up].sort_values(by='Volume', ascending=False) #.head(50)
   # r = tickers[tickers['Price (Intraday)'] < 10].sort_values(by='Volume').tail(3)
   print(r)
   return r

def get_high_change_ticker(tickers):
   positive_change = tickers['% Change'] > 0
   r = tickers[positive_change].sort_values(by='% Change', ascending=False) #.head(30)
   # r = r[r['Price (Intraday)'] < 50].sort_values(by='% Change').tail(3)
   print(r)
   return r

def get_ticker_w_unusual_volume(tickers):
   # tickers['temp'] = tickers['Volume'] / tickers['Avg Vol (3 month)'] 
   # r = tickers.sort_values(by=['temp'], ascending=False)
   # r = tickers.assign(temp = (tickers['Volume'] / tickers['Avg Vol (3 month)']) * 100 ).sort_values('temp', ascending=False).drop('temp', axis=1).head(20)
   
   r = tickers.assign(temp = (tickers['Volume'] / tickers['Avg Vol (3 month)']) * 100 )
   r = r[r['temp'] >= 90].sort_values('temp', ascending=False).drop('temp', axis=1)
   
   # r = tickers.sort_values(by='Volume', ascending=False).head(5)

   # r = tickers[tickers['Price (Intraday)'] < 10].sort_values(by='Volume').tail(3)
   print(r)
   return r

def set_buyin_per_tic(tickers):
   total_weight = 100
   min_weight = 10

   if len(tickers.index) >= 4:
      weight = 40
   elif len(tickers.index) == 3 :
       weight = 50
   elif len(tickers.index) == 2 :
       weight = 60
   for symbol, price in zip(tickers['Symbol'], tickers['Price (Intraday)']):
      print (symbol, price, weight)
      weight = weight - min_weight


def get_open_position(tickers):
   return 'a'



r = get_ticker_by_volume(r, 10)
r = get_high_change_ticker(r)

# set_buyin_per_tic(r)
print (r)
# r = get_ticker_w_unusual_volume(r)



# todo
# get top 10 ticker by vol/avg.vol
# get top 10 ticker by volume
# get top 10 ticker by % change



