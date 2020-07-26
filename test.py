import requests
import time
from datetime import datetime, timedelta
import pytz
import pandas as pd
import asyncio
from requests_html import HTMLSession
from aiohttp import ClientSession

BASE_URL ='https://query1.finance.yahoo.com/v8/finance/chart/'
df = pd.DataFrame(columns=["symbol, ""open", "high", "low", "close", "volume"])
mydf = pd.DataFrame(columns=["symbol, ""open", "high", "low", "close", "volume"])

def force_float(elt):
    
    try:
        return float(elt)
    except:
        return elt

def _raw_get_daily_info(site):
    session = HTMLSession()
    resp = session.get(site)
    tables = pd.read_html(resp.html.raw_html)  
    df = tables[0].copy()
    df.columns = tables[0].columns
    del df["52 Week Range"]
    df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%")))
    fields_to_change = [x for x in df.columns.tolist() if "Vol" in x \
                        or x == "Market Cap"]
    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].str.strip("B").map(force_float)
            df[field] = df[field].map(lambda x: x if type(x) == str 
                                                else x * 1000000000)
            df[field] = df[field].map(lambda x: x if type(x) == float else
                                    force_float(x.strip("M")) * 1000000)    
    session.close()
    return df
    
def get_day_most_active(price):
    tickers = _raw_get_daily_info("https://finance.yahoo.com/most-active?offset=0&count=100")
    below_cap_price = tickers['Price (Intraday)'] <= price
    # volume = tickers['Volume'] >= 5000000
    # vol_up = tickers['Volume'] < 1000000000
    # r = tickers[below_cap_price & volume & vol_up].sort_values(by='Volume', ascending=False) #.head(50)
    # return r
    return tickers[below_cap_price]

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
                # print(data["chart"]["result"][0]["indicators"]["quote"][0])
                r={}
                r["symbol"] = ticker
                r["close"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["close"][0]
                r["low"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["low"][0]
                r["high"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["high"][0]
                r["volume"] = data["chart"]["result"][0]["indicators"]["quote"][0]["volume"][0]
                r["timestamp"]= data["chart"]["result"][0]["timestamp"][0]
                r["easterntime"] = (datetime.datetime.fromtimestamp(data["chart"]["result"][0]["timestamp"][0])).astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
                file_res = open("tuesday.txt", "a")
                file_res.writelines("," + str(r) +"\n")
                file_res.close()
                # print(r)
                # frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
                
                # get the date info
                # temp_time = data["chart"]["result"][0]["timestamp"]

                # frame[] = pd.to_datetime(temp_time, unit = "s")
                # frame = frame[["open", "high", "low", "close", "volume"]]
                # frame.index = frame.index.map(lambda dt: dt.floor("d"))
                # print(ticker, frame)
                
            # else:
            #     frame = pd.DataFrame(columns=['pos', 'symbol', 'price', 'time'])
            #     frame.loc[data["chart"]["result"][0]["meta"]["regularMarketTime"]] = [0, ticker, data["chart"]["result"][0]["meta"]["regularMarketPrice"], data["chart"]["result"][0]["meta"]["regularMarketTime"]]
            #     print(frame)
            # return frame

async def get_tickers_price(tickers):
    await asyncio.wait([get_price(ticker) for ticker in tickers])

async def get_history_price(ticker, range_day=1, start_sec=None, interval=None):
    if start_sec is None:
        start_seconds = int(time.time()) - (range_day * 86400)
    
    end_seconds = start_seconds + (range_day * 86400) + 3600
    if range_day <= 7:
        if interval is None:
            interval = "1m"
        elif interval not in ("1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"):
            raise AssertionError("interval valid : 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h")
    elif range_day <= 60:
        if interval is None:
            interval = "2m"
        elif interval not in ("2m", "5m", "15m", "30m", "60m", "1h", "90m", "1d", "5d", "1wk"):
            raise AssertionError("interval valid : 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk")
    elif range_day <= 730:
        if interval is None:
            interval = "1h"
        elif interval not in ("60m", "1h", "90m", "1d", "5d", "1wk", "1mo", "3mo"):
            raise AssertionError("interval valid : 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    else:
        raise AssertionError("range_day max is 730 days")

    range_s = str(range_day) + "d"
    params = {"period1": start_seconds, "period2": end_seconds, "interval" : interval, "range" : range_s}
    site = BASE_URL + ticker
    async with ClientSession() as session:
        resp = await session.request(method="GET", url=site, params=params, ssl= False)
        data = await resp.json()
        frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
        temp_time = data["chart"]["result"][0]["timestamp"]
        frame['eastern_time'] = (datetime.datetime.fromtimestamp(data["chart"]["result"][0]["timestamp"][0])).astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")

        frame.index = pd.to_datetime(temp_time, unit = "s")
        frame = round(frame[["open", "high", "low", "close", "volume", "eastern_time"]],2)
        # frame.index = frame.index.map(lambda dt: dt.floor("d"))
        frame.to_json("training.data.txt")

async def get_training_data(ticker):
    tz = pytz.timezone('US/Eastern')
    # usTime = datetime.now(tz)
    usTime = datetime(2020,5,20, 9,30, tzinfo=tz)
    
    start= int(usTime.timestamp())
    eod= int((usTime + timedelta(hours=7)).timestamp())
    fileName = usTime.strftime('%Y%m%d') + '.td.txt'
    params = {"period1": start, "period2": eod, "interval" : '1m', "range" : '1d'}
    # site='https://query1.finance.yahoo.com/v8/finance/chart/?symbol=' + ticker + '&period1='+ str(start) + '&period2='+ str(eod) + '&interval=1m&range=1d'
    site=BASE_URL + ticker
    async with ClientSession() as session:
        resp = await session.request(method="GET", url=site, params=params, ssl= False)
        data = await resp.json()
        frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
        frame = frame.round(2)
        frame['timestamp'] = data["chart"]["result"][0]["timestamp"]
        # frame.index = pd.to_datetime(temp_time, unit = "s")
        frame['symbol'] = ticker
        frame = frame[["timestamp", "symbol", "open", "high", "low", "close", "volume"]]
        frame.to_json(fileName, orient='split')

async def main():
    tz = pytz.timezone('US/Eastern')
    usTime = datetime.datetime.now(tz)
    waits = int((datetime.datetime(usTime.year, usTime.month, usTime.day, 9, 30, tzinfo=usTime.tzinfo) - datetime.datetime.now(tz)).total_seconds())+3
    await asyncio.sleep(waits)

    start_time = int(time.time())
    tickers = (get_day_most_active(10))["Symbol"].values.tolist()
    last_refresh = int(time.time())
    prev=None
    # await asyncio.sleep(1800)
    while True:
        prev = int(time.time())
        print('> requesting', str(prev)[-2:])
        await get_tickers_price(tickers)
        print('< responded', str(int(time.time()))[-2:])
        if (int(time.time()) -last_refresh) >= 60:
                print('refreshing active stocks', last_refresh)
                tickers += (get_day_most_active(10))["Symbol"].values.tolist()
                tickers = list(dict.fromkeys(tickers))
                # tickers = tickers.drop_duplicates().values.tolist()
                last_refresh = int(time.time())
        
        if (int(time.time())-start_time) >= 28500:
            break
        else:
            waitSec = int(time.time()) - prev
            if waitSec > 0 and int(time.time()) != prev:
                waitSec = 5 - waitSec
                print('waiting...', waitSec)
                if waitSec > 0:
                    await asyncio.sleep(waitSec)
            elif int(time.time()) == prev:
                # print('waiting...', 4)
                await asyncio.sleep(5)
        
    # print(int(time.time()))
    # await get_price('MRO')
    # await get_history_price('ET', 2, interval="1m")

if __name__ == "__main__":
    # asyncio.run(main(), debug=True)
    # asyncio.run(main())
    asyncio.run(get_training_data('ET'), debug=True)
    