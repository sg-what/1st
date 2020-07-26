import matplotlib.pyplot as plt
import pandas as pd

axs = plt.gca()

df = pd.read_json('res.txt')
df['time'] = df.index
df['vol'] = df['volume']/1000000
df.plot(kind='line', x='time', y='open', ax=axs)
df.plot(kind='line', x='time', y='close', ax=axs)
df.plot(kind='line', x='time', y='vol', ax=axs)
plt.figure(figsize = (18,9))
plt.plot(range(df.shape[0]),(df['low']+df['high'])/2.0)
plt.plot(range(df.shape[0]),(df['volume'])/1000000)
plt.xticks(range(0,df.shape[0],1500),df['time'].loc[::1500],rotation=15)
plt.show()