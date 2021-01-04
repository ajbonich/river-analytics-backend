import datetime
import json
import numpy as np
import pandas as pd
import urllib3

# Uncomment if graphs need to be tested locally for some reason
# import matplotlib.dates as mdates
# import matplotlib.pyplot as plt
# from pandas.plotting import register_matplotlib_converters

# TODO: make a call to get the period data is available

# default data
defaultUseTestData = True
defaultSiteId = '06719505'  # Clear Creek at Golden
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2100, 12, 31)
defaultParameter = '00060'  # cubic feet per second (cfs)
defaultMinFlow = 300
defaultMaxFlow = 1000

defaultStatsDate = datetime.date(1000, 6, 4)

# app = Flask(__name__)


# @app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    return response

# test from console with exec(open('usgs-controller.py').read())


# @app.route('/')
def getUSGSDefaultData(event, object):
    cleanData = cleanUSGSData(getUSGSData())
    print('Data cleaned')
    avg = cleanData.mean(axis=1)
    return formatOutput(avg)


# @app.route('/getDailyAverageData')
def getDailyAverageData(event, object):
    '''Makes a usgs call with given or default parameters to create a clean dataframe object
    '''
    try:
        siteId = event['queryStringParameters']['siteId']
    except:
        siteId =  defaultSiteId
    
    try:
        startDate = event['queryStringParameters']['startDate']
    except:
        startDate = defaultStartDate # included for future ability to filter on years
    
    try:
        endDate = event['queryStringParameters']['endDate']
    except:
        endDate = defaultEndDate # included for future ability to filter on years
    
    try:
        gaugeParameter = event['queryStringParameters']['gaugeParameter']
    except:
        gaugeParameter = defaultParameter # included for future ability to use other params
    
    try:
        testDataFlag = event['queryStringParameters']['testDataFlag']
    except:
        testDataFlag = False
    
    data = getUSGSData(testDataFlag, siteId, startDate,
                       endDate, gaugeParameter)
    cleanData = cleanUSGSData(data)
    returnData = pd.DataFrame(cleanData.mean(axis=1), columns=['average'])
    returnData['quantile20'] = cleanData.quantile(0.2, axis=1)
    returnData['quantile80minus20'] = cleanData.quantile(
        0.8, axis=1) - returnData['quantile20']
    return formatOutput(returnData)


# @ app.route('/getRunnablePercentages')
def getDailyRunnablePercentage(event, object):
    '''Takes in a mimimum and maximum value for the section and returns
    a graph displaying the odds the section is runnable for each day
    '''

    try: 
        siteId = event['queryStringParameters']['siteId']
    except:
        siteId = defaultSiteId
  
    try: 
        minFlow = int(event['queryStringParameters']['minFlow'])
    except:
        minFlow = defaultMinFlow

    try: 
        maxFlow = int(event['queryStringParameters']['maxFlow'])
    except:
        maxFlow = defaultMaxFlow

    try:
        testDataFlag = event['queryStringParameters']['testDataFlag']
    except:
        testDataFlag = False

    data = getUSGSData(testDataFlag, siteId)
    averageData = cleanUSGSData(data)

    countInRange = averageData[(averageData > minFlow) & (averageData < maxFlow)].count(axis=1)
    totalCount = averageData[averageData > 0].count(axis=1)
    dailyPercent = countInRange.div(totalCount)
    # daysOver50 = percentages[percentages > 50]

    return formatOutput(dailyPercent * 100)  

def formatOutput(data, decimals: int = 0):
    '''Creates json dictionary with value label on value objects
    '''
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': data.round(1).reset_index().to_json(orient='records')
    }
    
    return response


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