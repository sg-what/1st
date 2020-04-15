import asyncio
import datetime
import pytz
import time
import json

import alpaca as al
import most_active as ma

def stopwatch(start=0):
   if start==0:
      return time.perf_counter()
   else:
      return time.perf_counter()-start

async def get_posistion(pd):
   buy = 0
   sell = 0
   if pd.loc[3]['price'] > pd.loc[0]['price']:
      buy = buy + 2
   else:
      buy = buy -2
   if pd.loc[0]['price'] < pd.loc[6]['price']:
      buy = buy + 1
   else:
      buy = buy -1
   if pd.loc[3]['price'] < pd.loc[6]['price']:
      buy = buy + 1
   else:
      buy = buy -1
   if pd.loc[0]['price'] < pd.loc[9]['price']:
      buy = buy + 1
   else:
      buy = buy -1
   
   if buy >= 3:
      order = al.post_orders(pd.loc[3]['symmbol'], 303, 'buy,', 'market','day')
      print(order)

async def set_position(pd):
   my_orders = await al.post_orders(pd.loc[3]['symmbol'], 303, 'buy,', 'market','day')

async def monitor_price(symbol_list, pos):
   for symbol in symbol_list:
      ma.get_price(symbol, pos)
      # now = datetime.datetime.now(pytz.utc)
      # nows = (now.astimezone(pytz.timezone('US/Eastern'))).strftime("%H:%M:%S.%f")[:-3]
      # print(pos, nows, symbol)

async def main():
   start=stopwatch()
   my_account = await al.get_account()
   my_orders = await al.get_orders()
   my_positions = await al.get_positions()
   
   if my_positions:
      print('not empty')
   else:
      tickers = await ma.get_tickers(10)
      
      ticker_list = tickers['Symbol'].values.tolist()
      # await asyncio.wait([monitor_price(symbol) for symbol, price in zip(tickers['Symbol'], tickers['Price (Intraday)'])])
      # for pos in range(10):
      await asyncio.wait([monitor_price(ticker_list, pos) for pos in range(10)])
      

      await asyncio.wait([get_posistion(ma.df[ma.df['symbol'] == symbol]) for symbol in ticker_list])
      # ticker_df = ma.df[ma.df['symbol'] == symbol]
      # await get_posistion(ticker_df)
   
   my_orders = await al.get_orders()
   print(my_account)
   print(my_orders)
   print(my_positions)

   end=stopwatch(start)
   print(f"duration {end:0.2f} second")
   return my_orders
   # while True:


if __name__ == "__main__":
   asyncio.run(main())
   