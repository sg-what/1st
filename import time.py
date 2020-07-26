import time
import datetime
import pytz
import pandas as pd
import asyncio
from requests_html import HTMLSession
from aiohttp import ClientSession

df = pd.DataFrame(columns=["symbol, ""open", "high", "low", "close", "volume"])

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