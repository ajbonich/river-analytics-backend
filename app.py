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
#from pandas.plotting import register_matplotlib_converters

# TODO: make a call to get the period data is available

# default data
defaultUseTestData = True
defaultSiteId = '06719505'  # Clear Creek at Golden
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2100, 12, 31)
defaultParameter = '00060'  # cubic feet per second (cfs)

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
    return formatUSGSData(getUSGSData())


@app.route('/getDailyAverageData')
def getDailyAverageData() -> json:
    '''Makes a usgs call with given or default parameters to create a clean dataframe object
    '''

    siteId = request.args.get('siteId') or defaultSiteId
    startDate = request.args.get('startDate') or defaultStartDate
    endDate = request.args.get('endDate') or defaultEndDate
    gaugeParameter = request.args.get('gaugeParameter') or defaultParameter

    if request.args.get('useTestData') == 'True':
        with open('testFile.json') as tf:
            print('Using test data.')
            data = json.load(tf)
    else:
        data = getUSGSData(False, siteId, startDate, endDate, gaugeParameter)

    return formatUSGSData(data)


def getUSGSData(useTestData: bool = defaultUseTestData,
                siteId: str = defaultSiteId,
                startDate: datetime.date = defaultStartDate,
                endDate: datetime.date = defaultEndDate,
                gaugeParameter: str = defaultParameter) -> json:
    '''Call USGS
    '''

    url = f'https://waterservices.usgs.gov/nwis/dv/?format=json&site={siteId}&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}'
    response = requests.get(url)
    responseJson = response.json()
    # may have to change this if the json format is different
    valueData = responseJson['value']['timeSeries'][0]['values'][0]['value']

    return valueData


def formatUSGSData(jsonData):
    '''Format USGS Data
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
    avg = df.mean(axis=1)
    avg = avg.to_frame('value')

    return avg.reset_index().to_json(orient='records')


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


def getDailyRunnablePercentages(df: pd.DataFrame = pd.read_json(getUSGSDefaultData()), minimumRunnable: int = 300):
    ''Takes in a dataframe and a minimum for the section and returns
a graph displaying the odds the section is runnable for each day
''

    def f(row): return (row > minimumRunnable).mean()
    percentages = df.apply(f)
    daysOver50 = percentages[percentages > 50]
    return percentages, daysOver50
'''

if __name__ == '__main__':
    app.run(debug=True, port=8888)
