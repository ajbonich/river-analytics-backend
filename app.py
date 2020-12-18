import datetime, json, requests
import numpy as np
import pandas as pd
from flask import Flask
from flask import request
from flask import jsonify

# Uncomment if graphs need to be tested locally for some reason
# import matplotlib.dates as mdates
# import matplotlib.pyplot as plt
#from pandas.plotting import register_matplotlib_converters

#TODO: make a call to get the period data is available

#default data
defaultUseTestData = True
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2020, 10, 25)
defaultSiteId = '06719505' #Clear Creek at Golden
defaultParameter = '00060' #cubic feet per second (cfs)

defaultStatsDate = datetime.date(1000, 6, 4)

app = Flask(__name__)
@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    return response

#test from console with exec(open('usgs-controller.py').read())
@app.route('/')
def getDailyAverageData(useTestData: bool = defaultUseTestData,
                        startDate: datetime.date = defaultStartDate, 
                        endDate: datetime.date = defaultEndDate, 
                        siteId: str = defaultSiteId, 
                        gaugeParameter: str = defaultParameter) -> json:
    '''Makes a usgs call with given or default parameters to create a clean dataframe object
    '''
    
    if useTestData:
        with open('testFile.json') as tf:
            print('Using test data.')
            valueData = json.load(tf)
    else:
        url = f'https://waterservices.usgs.gov/nwis/dv/?format=json&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}&site={siteId}'
        response = requests.get(url)
        responseJson = response.json()
        valueData = responseJson['value']['timeSeries'][0]['values'][0]['value'] #may have to change this if the json format is different

    df = pd.DataFrame(valueData)
    df = df.drop('qualifiers', axis=1)
    df['value'] = df['value'].astype(float)
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    months, days, years = zip(*[(d.month, d.day, d.year) for d in df['dateTime']])
    df = df.assign(month=months, day=days, year=years)
    df = df.drop('dateTime', axis=1)
    df = df.pivot(index=['month', 'day'], columns='year', values='value')
    df = df.T
    
    return df.to_json() 
    

#input a df and a date
@app.route('/getDailyStatistics', methods=['GET'])
def getDailyStatistics(df: pd.DataFrame = pd.read_json(getDailyAverageData()), userDate: datetime.date = defaultStatsDate, minimumRunnable: int = 300) -> pd.Series:
    '''Takes in a dataframe and a date to return the average flow, 
    percent of years above the minimum, and the standard deviation flow
    '''

    dayMean = df[(userDate.month, userDate.day)].mean()
    yearsRunnable = len(df[df[(userDate.month, userDate.day)] > minimumRunnable])
    totalYears = len(df)
    percentageOfYearsRunnable = 100 * yearsRunnable / totalYears
    standardDeviation = df[(userDate.month, userDate.day)].std()

    return pd.Series([dayMean, percentageOfYearsRunnable, standardDeviation], index=['mean', 'percentageOfYearsRunnable', 'standardDeviation'])

    
def getDailyRunnablePercentages(df: pd.DataFrame = pd.read_json(getDailyAverageData()), minimumRunnable: int = 300):
    '''Takes in a dataframe and a minimum for the section and returns
    a graph displaying the odds the section is runnable for each day
    '''

    f = lambda row: (row > minimumRunnable).mean()
    percentages = df.apply(f)
    daysOver50 = percentages[percentages > 50]
    return percentages, daysOver50

# # Basic chart
# # df=pd.DataFrame({'x': range(1,101), 'y': np.random.randn(100)*15+range(1,101) })
# fig, (runnableGraph, flowGraph) = plt.subplots(2, sharex=True)
# plt.xlabel('Date')
# plt.ylabel('Streamflow (cfs)')
# runnableGraph.set_title('CC Golden Daily average cfs')
# runnableGraph.plot(dates, runnableRate)
# runnableGraph.set_ylabel('Percent of time runnable')
# flowGraph.plot(dates, flow, marker='o', markersize=1)

# plt.show()


if __name__ == '__main__':
    app.run(debug=True, port=8888)