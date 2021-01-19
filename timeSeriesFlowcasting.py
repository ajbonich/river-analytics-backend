from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.ar_model import AutoReg
from random import random

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


train = pd.read_csv('trainData.csv')
test = pd.read_csv('testData.csv')
train['dateTime'] = pd.to_datetime(train['dateTime'])
test['dateTime'] = pd.to_datetime(test['dateTime'])
train.set_index('dateTime', inplace=True)
test.set_index('dateTime', inplace=True)
df = train.copy()
df = df.asfreq('d')
df = df.bfill()

# Showing seasonality
'''
plt.rcParams.update({'figure.figsize': (9, 5)})
autocorrelation_plot(df.value.tolist())
plt.show()
'''

# Calculate ACF and PACF upto 50 lags
# acf_50 = acf(df.value, nlags=50)
# pacf_50 = pacf(df.value, nlags=50)

fig, axes = plt.subplots(1, 2, figsize=(16, 3), dpi=100)
plot_acf(df.value.tolist(), lags=50, ax=axes[0])
plot_pacf(df.value.tolist(), lags=50, ax=axes[1])
plt.show()

# Analyzing stationary
'''
from statsmodels.tsa.stattools import adfuller
result = adfuller(df.value.values, autolag='AIC')
print(f'ADF Statistic: {result[0]}')
print(f'p-value: {result[1]}')
for key, value in result[4].items():
    print('Critial Values:')
    print(f'   {key}, {value}')
'''

# Decomposition
'''
from statsmodels.tsa.seasonal import seasonal_decompose
result_mul = seasonal_decompose(
    df['value'], model='multiplicative', extrapolate_trend='freq')
result_add = seasonal_decompose(
    df['value'], model='additive', extrapolate_trend='freq')
plt.rcParams.update({'figure.figsize': (10, 10)})
result_mul.plot().suptitle('Multiplicative Decompose', fontsize=22)
result_add.plot().suptitle('Additive Decompose', fontsize=22)
plt.show()

#Showing the decomp
df_reconstructed = pd.concat(
    [result_mul.seasonal, result_mul.trend, result_mul.resid, result_mul.observed], axis=1)
df_reconstructed.columns = ['seas', 'trend', 'resid', 'actual_values']
df_reconstructed.head()
'''

# train.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# test.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# plt.show()

# sm.tsa.seasonal_decompose(df.value).plot()
# result = sm.tsa.stattools.adfuller(df.value)
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
