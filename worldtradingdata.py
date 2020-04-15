import requests

rq = requests.get('https://api.worldtradingdata.com/api/v1/stock?symbol=SNAP,TWTR,VOD.L&api_token=demo')
print(rq.json())
r