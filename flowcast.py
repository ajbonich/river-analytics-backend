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
#from sklearn.metrics import mean_squared_error
from math import sqrt

# default data
defaultUseTestData = False
defaultSiteId = '06719505'  # Clear Creek at Golden
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2100, 12, 31)
defaultParameter = '00060'  # cubic feet per second (cfs)
defaultMinFlow = 300
defaultMaxFlow = 1000

defaultStatsDate = datetime.date(1000, 6, 4)


def getUSGSData(useTestData: bool = defaultUseTestData,
                siteId: str = defaultSiteId,
                startDate: datetime.date = defaultStartDate,
                endDate: datetime.date = defaultEndDate,
                gaugeParameter: str = defaultParameter) -> json:
    '''Call USGS or get test data
    '''

    if useTestData:
        with open('testFile.json') as tf:
            print('Using test data.')
            return json.load(tf)

    url = f'http://waterservices.usgs.gov/nwis/dv/?format=json&site={siteId}&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}'
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    responseJson = json.loads(response.data.decode('utf-8'))
    # may have to change this if the json format is different
    valueData = responseJson['value']['timeSeries'][0]['values'][0]['value']

    return valueData

def generateCSV():
    jsonData = getUSGSData()
    df = pd.DataFrame(jsonData)
    df = df.drop('qualifiers', axis=1)
    df['value'] = df['value'].astype(float)
    df['dateTime'] = pd.to_datetime(df['dateTime'])   
    df[df['value'] <= 0] = np.nan
    train = df[0:16500]
    train.index = train.dateTime
    test = df[16500:]
    test.index = test.dateTime
    train.to_csv('trainData.csv')
    test.to_csv('testData.csv')
    # train.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
    # test.value.plot(figsize=(15,8), title= 'Golden Flow History', fontsize=14)
    # plt.show()
    # return df, train, test

def cleanUSGSData(jsonData):
    '''Clean USGS Data
    '''
    df = pd.DataFrame(jsonData)
    df = df.drop('qualifiers', axis=1)
    df['value'] = df['value'].astype(float)
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    months, days, years = zip(*[(d.month, d.day, d.year)
                                for d in df['dateTime']])
    df = df.assign(month=months, day=days, year=years)
    df = df.drop('dateTime', axis=1)
    df = df.pivot(index=['month', 'day'], columns='year', values='value')
    df.index = df.index.map(lambda t: f'{t[0]}/{t[1]}')
    df[df <= 0] = np.nan
    return df

# usgsData, data2 = cleanUSGSData(getUSGSData())
# data = [x + random() for x in range(1, 100)]
# # fit model
# model = AutoReg(data, lags=1)
# model_fit = model.fit()
# # make prediction
# yhat = model_fit.predict(len(data), len(data))
# print(yhat)
