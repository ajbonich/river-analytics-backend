import datetime, json, matplotlib, requests
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from pandas.plotting import register_matplotlib_converters

#TODO: make a call to get the period data is available

#default data
useTestData = True
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2020, 10, 25)
defaultSiteId = '06719505' #Clear Creek at Golden
defaultParameter = '00060' #cubic feet per second (cfs)

defaultStatsDate = datetime.date(1000, 6, 4)

#test from console with exec(open('usgs-controller.py').read())
def getDailyAverageData(useTestData: bool = False,
                        startDate: datetime.date = defaultStartDate, 
                        endDate: datetime.date = defaultEndDate, 
                        siteId: str = defaultSiteId, 
                        gaugeParameter: str = defaultParameter) -> pd.DataFrame:
    '''Makes a usgs call with given or default parameters to create a clean dataframe object
    '''

    if useTestData:
        with open('testFile.json') as tf:
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
    
    return df   

#input a df and a date
def getDailyStatistics(df: pd.DataFrame = getDailyAverageData(), userDate: datetime.date = defaultStatsDate, minimumRunnable: int = 300) -> pd.Series:
    '''Takes in a dataframe and a date to return the average flow, 
    percent of years above the minimum, and the standard deviation flow
    '''

    dayMean = df[(userDate.month, userDate.day)].mean()
    yearsRunnable = len(df[df[(userDate.month, userDate.day)] > minimumRunnable])
    totalYears = len(df)
    percentageOfYearsRunnable = 100 * yearsRunnable / totalYears
    
    return pd.Series([dayMean, percentageOfYearsRunnable], index=['mean', 'percentageOfYearsRunnable'])

    

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