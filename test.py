# import requests
import time
import datetime
import pytz
import pandas as pd
import asyncio
from requests_html import HTMLSession
from aiohttp import ClientSession

df = pd.DataFrame(columns=["symbol, ""open", "high", "low", "close", "volume"])

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
    volume = tickers['Volume'] >= 10000000
    vol_up = tickers['Volume'] < 1000000000
    r = tickers[below_cap_price & volume & vol_up].sort_values(by='Volume', ascending=False) #.head(50)
    return r

async def get_price(ticker, interval_type=None, start_sec=None):
    """
    # interval_type : 1d", "5d", "1mo", "3mo","6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    """
    base_url ='https://query1.finance.yahoo.com/v8/finance/chart/'
    # start_seconds = int(time.time()) - 386400
    if interval_type is None:
        interval_type = "1d"
        start_seconds = int(time.time()) - 3
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
    site = base_url + ticker
    # resp = requests.get(site, params = params)
    async with ClientSession() as session:
        resp = await session.request(method="GET", url=site, params=params)
        # resp = await session.request(method="GET", url=site)
    # if not resp.ok:
    #     raise AssertionError(resp.json())
        if resp.status == 200:
            data = await resp.json()

            if data["chart"]["result"][0]["indicators"]["quote"][0]:
                # print(data["chart"]["result"][0]["indicators"]["quote"][0])
                r={}
                r["symbol"] = ticker
                r["price"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["close"][0]
                r["low"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["low"][0]
                r["high"] = "%.2f" % data["chart"]["result"][0]["indicators"]["quote"][0]["high"][0]
                r["volume"] = data["chart"]["result"][0]["indicators"]["quote"][0]["volume"][0]
                r["timestamp"] = (datetime.datetime.fromtimestamp(data["chart"]["result"][0]["timestamp"][0])).astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
                file_res = open("res.txt", "a")
                file_res.writelines("," + str(r) +"\n")
                file_res.close()
                # print(r)
                # frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
                
                # get the date info
                # temp_time = data["chart"]["result"][0]["timestamp"]

                # frame.index = pd.to_datetime(temp_time, unit = "s")
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

async def get_history_price(ticker, range_day=1 start_sec=None, interval=None):
    if start_sec is None:
        start_sec = int(time.time()) - (range_day * 86400)
    
    end_sec = start_sec + (range_day * 86400) + 3600
    if range_day <= 7:
        if interval is None:
            interval = "1m"
        elif interval not in ("1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"):
            raise AssertionError("interval valid : 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h")
    if range_day <= 60:
        if interval is None:
            interval = "2m"
        elif interval not in ("2m", "5m", "15m", "30m", "60m", "1h", "90m", "1d", "5d", "1wk"):
            raise AssertionError("interval valid : 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk")
    if range_day <= 730:
        if interval is None:
            interval = "1h"
        elif interval not in ("60m", "1h", "90m", "1d", "5d", "1wk", "1mo", "3mo"):
            raise AssertionError("interval valid : 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    else:
        raise AssertionError("range_day max is 730 days")

    range_s = str(range_day_day) + "d"
    params = {"period1": start_seconds, "period2": end_seconds, "interval" : interval_type, "range_day" : range_s}
    async with ClientSession() as session:
        resp = await session.request(method="GET", url=site, params=params)
        data = await resp.json()
        frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
        temp_time = data["chart"]["result"][0]["timestamp"]

        frame.index = pd.to_datetime(temp_time, unit = "s")
        frame = frame[["open", "high", "low", "close", "volume"]]
        frame.index = frame.index.map(lambda dt: dt.floor("d"))
        file_res = open("{}.txt".format(ticker), "w")
        file_res.writelines(data)
        file_res.close()

async def main():
    start_time = int(time.time())
    tickers = (get_day_most_active(10))["Symbol"].values.tolist()
    last_refresh = int(time.time())
    while True:
        await get_tickers_price(tickers)
        if (last_refresh - int(time.time())) > 300:
            tickers = (get_day_most_active(10))["Symbol"].values.tolist()
            last_refresh = int(time.time())
        else:
            await asyncio.sleep(3)
        
        if (int(time.time())-start_time) >= 1440:
            break
        
    print(int(time.time()))
    # await get_price('MRO')
    

if __name__ == "__main__":
    # asyncio.run(main(), debug=True)
    asyncio.run(main())
    # main()