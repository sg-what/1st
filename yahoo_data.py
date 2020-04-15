import yfinance as yf
# from yfinance import stock_info

# yf.get_day_most_active()
msft = yf.Ticker("AAPL")

hist = msft.history(period="1d", interval="1m")
print(list(hist.columns.values))
# print(hist)
data = hist.between_time("10:01:10", "11:02:12")
# print(data[['Volume', 'Open']])
print(data)
