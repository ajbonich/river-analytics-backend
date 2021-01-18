# AR example
from statsmodels.tsa.ar_model import AutoReg
from random import random
# contrived dataset

import datetime
import json
import numpy as np
import pandas as pd
import urllib3
import matplotlib.pyplot as plt
from statsmodels.tools.eval_measures import rmse
# from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import statsmodels.api as sm

from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse

train = pd.read_csv('trainData.csv')
test = pd.read_csv('testData.csv')
train['dateTime'] = pd.to_datetime(train['dateTime'])
test['dateTime'] = pd.to_datetime(test['dateTime'])
df = train
df = df.asfreq('d')
# Multiplicative Decomposition
# result_mul = seasonal_decompose(
#     df['value'], model='multiplicative', extrapolate_trend='freq')

# # Additive Decomposition
# result_add = seasonal_decompose(
#     df['value'], model='additive', extrapolate_trend='freq')

# # Plot
# plt.rcParams.update({'figure.figsize': (10, 10)})
# result_mul.plot().suptitle('Multiplicative Decompose', fontsize=22)
# result_add.plot().suptitle('Additive Decompose', fontsize=22)
# plt.show()

# train.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# test.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# plt.show()

# sm.tsa.seasonal_decompose(train.value).plot()
# result = sm.tsa.stattools.adfuller(train.value)
# plt.show()
'''
y_hat_avg = test.copy()
fit1 = sm(train.value, order=(2, 1, 4), seasonal_order=(0, 1, 1, 7)).fit()
y_hat_avg['SARIMA'] = fit1.predict(
    start="2013-11-1", end="2013-12-31", dynamic=True)
plt.figure(figsize=(16, 8))
plt.plot(train['value'], label='Train')
plt.plot(test['value'], label='Test')
plt.plot(y_hat_avg['SARIMA'], label='SARIMA')
plt.legend(loc='best')
plt.show()

rms = sqrt(mean_squared_error(test.value, y_hat_avg.Holt_Winter))
print(rms)
'''
