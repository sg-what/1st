import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib
import pandas as pd
import datetime
import time
import pytz


import numpy as np
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV as rcv
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from IPython import get_ipython

# tz=pytz.timezone('US/Eastern')

df = pd.read_json('res.txt')
df.fillna(df.mean(), inplace=True)
# df.iloc(dfa.index) = dfa
# df.fillna(df.mean(), inplace=True)

# df.index = df.index.tz_localize(tz='UTC')
# df.index = df.index.tz_convert('US/Eastern')
df['Open']=df['open'].shift(1)
df['High']=df['high'].shift(1)
df['Low']=df['low'].shift(1)
df['Close']=df['close'].shift(1)

imp = SimpleImputer(missing_values='NaN', strategy='mean')

steps = [('imputation', imp),
         ('scaler',StandardScaler()),
         ('lasso',Lasso())]        

pipeline =Pipeline(steps)


parameters = {'lasso__alpha':np.arange(0.0001,10,.0001),
              'lasso__max_iter':np.random.uniform(100,100000,4)}


reg = rcv(pipeline, parameters,cv=5)
X=df[['Open','High','Low','Close']]
y =df['close']

avg_err={}
print(df)
# for t in np.arange(50,97,3):
#     get_ipython().magic('reset_selective -f reg1')
#     split = int(t*len(X)/100)
#     reg.fit(X[:split],y[:split])
#     best_alpha = reg.best_params_['lasso__alpha']
#     best_iter= reg.best_params_['lasso__max_iter']
#     reg1= Lasso(alpha=best_alpha,max_iter=best_iter)
#     X=imp.fit_transform(X,y)
#     reg1.fit(X[:split],y[:split])