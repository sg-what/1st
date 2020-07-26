import requests
import time
import datetime
import pytz
import pandas as pd
import asyncio
import json
from requests_html import HTMLSession
from aiohttp import ClientSession
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

pd.options.mode.chained_assignment = None  

BASE_URL ='https://query1.finance.yahoo.com/v8/finance/chart/'
journal = pd.DataFrame(columns=["easterntime", "buytime", "selld", "symbol", "buy", "sell", "pnl%", "pnl", "breason", "sreason", "l", "h", "r%", "rt", "closeData"])

async def get_price(ticker, interval_type=None, start_sec=None):
    """
    # interval_type : 1d", "5d", "1mo", "3mo","6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    """
    
    # start_seconds = int(time.time()) - 386400
    if interval_type is None:
        interval_type = "1d"
        if start_sec is None:
            start_seconds = int(time.time()) - 5
        else:
            start_seconds = start_sec
        end_seconds = int(time.time())
    else:
        if interval_type== "5d":
            end_seconds = start_seconds + (5 * 86400)
        elif interval_type== "1mo":
            end_seconds = start_seconds + 2592000
        elif interval_type== "3mo":
            end_seconds = start_seconds + 7776000
        elif interval_type== "6mo":
            end_seconds = start_seconds + 15552000
        elif interval_type== "1y":
            end_seconds = start_seconds + 31536000
        elif interval_type== "2y":
            end_seconds = start_seconds + 63072000
    
    # params = {"period1": start_seconds, "period2": end_seconds, "interval" : interval_type, "events": "div,splits"}
    params = {"startTime": start_seconds, "endTime": end_seconds, "interval" : interval_type}
    # ticker = "ET"
    site = BASE_URL + ticker
    # resp = requests.get(site, params = params)
    async with ClientSession() as session:
        resp = await session.request(method="GET", url=site, params=params, ssl= False)
        # resp = await session.request(method="GET", url=site)
    # if not resp.ok:
    #     raise AssertionError(resp.json())
        if resp.status == 200:
            data = await resp.json()

            if data["chart"]["result"][0]["indicators"]["quote"][0]:
                frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
                frame['timestamp'] = data["chart"]["result"][0]["timestamp"]
                frame['symbol'] = ticker
                frame['easterntime'] = (datetime.datetime.fromtimestamp(data["chart"]["result"][0]["timestamp"][0])).astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
                frame = frame[["symbol", "timestamp", "close", "high", "low", "volume", "easterntime"]]
                frame=frame.round(2)
                return frame
                # frame[] = pd.to_datetime(temp_time, unit = "s")
                
                # frame.index = frame.index.map(lambda dt: dt.floor("d"))
                # print(ticker, frame)
                
            # else:
            #     frame = pd.DataFrame(columns=['pos', 'symbol', 'price', 'time'])
            #     frame.loc[data["chart"]["result"][0]["meta"]["regularMarketTime"]] = [0, ticker, data["chart"]["result"][0]["meta"]["regularMarketPrice"], data["chart"]["result"][0]["meta"]["regularMarketTime"]]
            #     print(frame)
            # return frame

def sell(transactions, pchange, delta, price, hold_duration, reason, low, high):
    global journal
    journal.iat[transactions-1, 2] = hold_duration
    journal.iat[transactions-1, 5] = price
    journal.iat[transactions-1, 6] = pchange
    journal.iat[transactions-1, 7] = delta
    journal.iat[transactions-1, 9] = reason
    journal.iat[transactions-1, 10] = low
    journal.iat[transactions-1, 11] = high

def buy(b, pchange, reason, close_data, rt):
    global journal
    b["r%"] = pchange
    b["rt"] = rt
    b["closeData"] = close_data
    b["breason"] = reason
    b = b[["easterntime", "timestamp", "symbol", "close", "breason", "r%", "rt", "closeData"]]
    b.rename(columns={"close":"buy", "timestamp":"buytime"}, inplace=True)
    journal = journal.append(b, ignore_index=True)

async def offline_get_price(ticker, df, timestamp):
    fr = df.loc[df["symbol"]==ticker].sort_values(by='timestamp')
    fr = fr.loc[fr["timestamp"] >= timestamp+5][:1]
    return fr

def drop_frame(df, idx, all : bool = False):
    if (all and idx == 1) or (not all and idx == 6):
        df.drop(df.index[[0]], inplace=True)
    elif all and idx >1:
        df.drop(df[:idx].index, inplace=True)
    return df

async def main():
    df = pd.DataFrame(columns=["symbol", "timestamp", "close", "high", "low", "volume", "ustime", "delta"])
    x=0
    file = 'monday.txt'
    with open(file) as train_file:
        d = json.load(train_file)
    offline_price = round(pd.DataFrame(d).sort_values(by='timestamp'),2)
    d=''
    # offline_price = pd.read_json('monday copy.txt')
    # offline_price = round(offline_price.sort_values(by='timestamp'),2)
    # decide to buy
    my_pprofit=1.0
    my_plost=-1.0
    max_pprofit = 3.0
    cap_range_pchange = 0.5    # %
    cap_range_pchange_max = 2  # %
    cap_range_val = 0.03
    action=""
    price = high = x = transactions = counters = timestamp = 0
    holding_duration = 300
    max_holding_duration = 600
    lost_df= pd.DataFrame(columns=["timestamp", "lost"])
    pchange=0.00
    low = 30000000
    while True:
        # rDf = await get_price('ET')
        rDf = await offline_get_price('ET', offline_price, timestamp)
        counters+=1
        if rDf.shape[0] == 0:
            print(round(journal['pnl%'].sum(),2), 'P:', round(journal[journal['pnl%']>0]['pnl%'].sum(), 2), 'L:', round(journal[journal['pnl%']<0]['pnl%'].sum(),2))
            print(journal)
            break

        if x > 0:
            df = drop_frame(df, x, False)
        df=df.append(rDf, ignore_index=True)
        timestamp = df.iloc[-1]['timestamp']
        x=df.shape[0]-1
        if x < 1:
            continue

        df['delta'] = round(df['close'].diff(1), 2)
        endW = round(df.iloc[-1]['close'], 2)
        startW = round(df.iloc[1]['close'], 2)
        
        if low > endW:
            low = endW
        if high < endW:
            high = endW
            
        z = df['delta'] == 0
        m = df['delta'] < 0
        p = df['delta'] > 0
        pchange = round(((endW - startW) / startW)*100, 2)
        # delta = round(endW - startW, 2)
        range_min_last = round(df.iloc[-1]['close'] - df.iloc[x*-1:]['close'].min(), 2)

        if action=="":      #buy
            if cap_range_val * -1 <= range_min_last <= 0:     #last price movement negative
                continue
            
            # +:3 ++
            if df[p].shape[0] >= 3 and df[df['delta']>=-0.02].shape[0] == 0:
                reason = [[df[p].shape[0], round(df[z].shape[0]*0.1,1), df[m].shape[0]*-1]]
                action="buy"
            
            # +:2 and -:0
            elif df[p].shape[0] >= 2 and df[m].shape[0] == 0:
                if (cap_range_pchange <= pchange <= cap_range_pchange): # %price change in the range
                    action = 'buy'
                    reason = "%"
            elif ((0.02 <= range_min_last <= cap_range_val) \
                and df[z].shape[0] < 3) and df[p].shape[0] > 2:
                reason = "%"
                action="buy"
            
            if action == "buy":
                    price = endW
                    b = df[["symbol", "timestamp", "close", "low", "high", "volume", "easterntime"]][-1:]
                    b.reset_index(inplace=True)
                    close_data= [df["close"][1:x+1].to_numpy()]
                    rt =[df["delta"][1:x+1].to_numpy()] 
                    buy(b, pchange, reason, close_data, rt)
                    df = drop_frame(df, x, True)
                    x=0
                    startW=endW
                    # transaction_time = int(time.time())
                    transaction_time = int(b.iloc[-1]["timestamp"])
                    transactions+=1

        else:       #sell
            pchange= round(((endW - price)/price)*100, 2)
            b = df[["symbol", "timestamp", "close", "low", "high", "volume", "easterntime"]][-1:]
            b["estPnL"] = pchange
            delta = round(endW - price, 2)
            print(timestamp, pchange, price, endW, low, high)
            force_sell = selling = False
            # holding_sec = int(time.time()) - transaction_time
            # if df.shape[0] > 1:
            #     movement = round(df.iloc[-1]['close'] - df.iloc[-2]['close'], 2)
            # else:
            #     movement = 0
            holding_sec = int(b.iloc[-1]["timestamp"]) - transaction_time
            # if holding_sec >= holding_duration:
            #      if (avg < 0 and pchange < avg) or (avg >= 0 and pchange > avg):
            #         force_sell = True
            #         reason = 0
            lost_df = lost_df.append(b[["timestamp", "estPnL"]], ignore_index=True)
            # avg = round(lost_df["estPnL"].mean(),2)

            # if endW == low and holding_sec >= holding_duration:
            #     selling = True
            #     reason = "Low"
            # elif pchange > max_pprofit:
            #     selling = True
            #     reason = "High"
            if pchange >= my_pprofit and lost_df.iloc[-2]['estPnL'] == lost_df.iloc[-3]['estPnL'] and pchange >= lost_df.iloc[-2]['estPnL']:
                selling = True
                reason = "<5mi"
            # elif delta==-0.02 and df[m].shape[0] >= 2: #and holding_sec >= holding_duration:
            #     selling = True
            #     reason = "-.02"
            elif pchange <= -1 and lost_df.iloc[-3:]['estPnL'].mean() <= 0 and lost_df.iloc[-3:]['estPnL'].mean() <= -0.5:
                selling = True
                reason = "-01%"
            # elif pchange <= -1 :
            #     selling = True
            #     reason = "-01%"
            # elif holding_sec >= max_holding_duration:
            #     selling = True
            #     reason = "TL"
            # elif df[z].shape[0] > 3 and df[m].shape[0] == 1:
            #     selling = True
            #     reason = "000"
            # elif pchange > lost_df[-3:-1]['estPnL'].mean() and lost_df[-3:-1]['estPnL'].mean() < 0 and pchange > 0:
            #     selling = True
            #     reason = "~3"
            
            if selling or force_sell:
                hold_duration = b.iloc[-1]["timestamp"] - journal.iloc[-1]["buytime"]
                sell(transactions, pchange, delta, endW, hold_duration, reason, low, high)
                action=""
                startW = endW
                df = drop_frame(df, x, True)
                lost_df= pd.DataFrame(columns=["timestamp", "lost"])
                low = 30000000
                high = 0
                # print(journal[-1:])
                print(reason, ':', round(journal['pnl%'].sum(),2), 'P:', round(journal[journal['pnl%']>0]['pnl%'].sum(), 2), 'L:', round(journal[journal['pnl%']<0]['pnl%'].sum(),2))

if __name__ == "__main__":
    # asyncio.run(main(), debug=True)
    asyncio.run(main())