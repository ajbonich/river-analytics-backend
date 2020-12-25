import datetime
import json
import requests
import numpy as np
import pandas as pd
from flask import Flask
from flask import request
from flask import jsonify

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
defaultMinFlow = 400
defaultMaxFlow = 1500

defaultStatsDate = datetime.date(1000, 6, 4)

app = Flask(__name__)


@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    return response

# test from console with exec(open('usgs-controller.py').read())


@app.route('/')
def getUSGSDefaultData():
    cleanData = cleanUSGSData(getUSGSData())
    avg = cleanData.mean(axis=1)
    return formatOutput(avg)


@app.route('/getDailyAverageData')
def getDailyAverageData() -> json:
    '''Makes a usgs call with given or default parameters to create a clean dataframe object
    '''

    siteId = request.args.get('siteId') or defaultSiteId
    startDate = request.args.get('startDate') or defaultStartDate
    endDate = request.args.get('endDate') or defaultEndDate
    gaugeParameter = request.args.get('gaugeParameter') or defaultParameter
    testDataFlag = request.args.get('useTestData') == 'True'

    data = getUSGSData(testDataFlag, siteId, startDate,
                       endDate, gaugeParameter)
    cleanData = cleanUSGSData(data)
    returnData = pd.DataFrame(cleanData.mean(axis=1), columns=['average'])
    returnData['quantile20'] = cleanData.quantile(0.2, axis=1)
    returnData['quantile80'] = cleanData.quantile(0.8, axis=1)
    return formatOutput(returnData)


@ app.route('/getRunnablePercentages')
def getDailyRunnablePercentages():
    '''Takes in a mimimum and maximum value for the section and returns
    a graph displaying the odds the section is runnable for each day
    '''

    siteId = request.args.get('siteId') or defaultSiteId
    minFlow = float(request.args.get('minFlow') or defaultMinFlow)
    maxFlow = float(request.args.get('maxFlow') or defaultMaxFlow)
    testDataFlag = request.args.get('useTestData') == 'True'

    data = getUSGSData(testDataFlag, siteId)
    averageData = cleanUSGSData(data)

    # def f(row): return (row > minFlow).mean(axis=1)
    boolGrid = averageData.apply(lambda row: (row > minFlow) & (row < maxFlow))
    dailyPercent = pd.DataFrame(boolGrid.mean(axis=1), columns=['percent'])
    # daysOver50 = percentages[percentages > 50]

    return formatOutput(dailyPercent * 100)  # , daysOver50


def formatOutput(data, decimals: int = 0):
    '''Creates json dictionary with value label on value objects
    '''

    return data.round(1).reset_index().to_json(orient='records')


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

    url = f'https://waterservices.usgs.gov/nwis/dv/?format=json&site={siteId}&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}'
    response = requests.get(url)
    responseJson = response.json()
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
    df[df < 0] = np.nan
    return df


'''
# input a df and a date
@app.route('/getDailyStatistics', methods=['GET'])
def getDailyStatistics(df: pd.DataFrame = pd.read_json(getUSGSDefaultData()), userDate: datetime.date = defaultStatsDate, minimumRunnable: int = 300) -> pd.Series:
    ''Takes in a dataframe and a date to return the average flow,
percent of years above the minimum, and the standard deviation flow
''

    dayMean = df[(userDate.month, userDate.day)].mean()
    yearsRunnable = len(
        df[df[(userDate.month, userDate.day)] > minimumRunnable])
    totalYears = len(df)
    percentageOfYearsRunnable = 100 * yearsRunnable / totalYears
    standardDeviation = df[(userDate.month, userDate.day)].std()

    return pd.Series([dayMean, percentageOfYearsRunnable, standardDeviation], index=['mean', 'percentageOfYearsRunnable', 'standardDeviation'])
'''


if __name__ == '__main__':
    app.run(debug=True, port=8888)
