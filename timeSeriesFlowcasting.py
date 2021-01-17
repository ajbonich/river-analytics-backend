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
from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.statespace import SARIMAX as sm

train = pd.read_csv('trainData.csv')
test = pd.read_csv('testData.csv')
train['dateTime'] = pd.to_datetime(train['dateTime'])
test['dateTime'] = pd.to_datetime(test['dateTime'])
train.index = train.dateTime
train = train.drop('dateTime.1', axis=1)
test.index = test.dateTime
test = test.drop('dateTime.1', axis=1)
# train.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# test.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
# plt.show()

y_hat_avg = test.copy()
fit1 = sm(train.value, order=(2, 1, 4),seasonal_order=(0,1,1,7)).fit()
y_hat_avg['SARIMA'] = fit1.predict(start="2013-11-1", end="2013-12-31", dynamic=True)
plt.figure(figsize=(16,8))
plt.plot( train['value'], label='Train')
plt.plot(test['value'], label='Test')
plt.plot(y_hat_avg['SARIMA'], label='SARIMA')
plt.legend(loc='best')
plt.show()

rms = sqrt(mean_squared_error(test.value, y_hat_avg.Holt_Winter))
print(rms)