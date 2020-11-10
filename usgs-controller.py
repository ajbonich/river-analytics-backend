import requests
import matplotlib.pyplot as plt
from climata.usgs import DailyValueIO
import datetime as dt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np

register_matplotlib_converters()
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (20.0, 10.0)

# set parameters
nyears = 0.5
ndays = 365 * nyears
station_id = "09058000"
param_id = "00060"

#old way to set the date range
'''
datelist = pd.date_range(end=pd.datetime.today(), periods=ndays).tolist()
print(datelist)
print(f'{datelist[0]} {type(datelist[0])}')
print(f'{datelist[-1]} {type(datelist[-1])}')
'''


#make a call to get the period data is available

endDate = dt.datetime.today() 
startDate = endDate - dt.timedelta(days=300)

#stat service used to get max/min/avg value for that day over a period of years
#used to get avg value for that day from that days values
data = DailyValueIO(
    start_date=startDate,
    end_date=endDate,
    station=station_id,
    parameter=param_id,
)

#url = 'https://waterservices.usgs.gov/nwis/dv/?format=waterml%2C1.1&endDT=2020-10-27&parameterCd=00060&startDT=2019-10-26&site=09058000'
url = 'https://waterservices.usgs.gov/nwis/dv/?format=json&endDT=2020-10-27&parameterCd=00060&startDT=2019-10-26&site=09058000'

response = requests.get(url)
print(response.headers)
print(response.json())
#stuff = untangle.parse(response)
#print(stuff)

# create lists of date-flow values
d = '''
for series in data:
    print(series.site_code)
    print(series.variable_code)
    for row in series.data:
        print(row.date)
        print(row.value)
    #print(series)
    #flow = [r[1] for r in series.data]
    #print(flow)
    #dates = [r[0] for r in series.data]
    #print(dates)




#plt.plot(dates, flow)
plt.xlabel('Date')
plt.ylabel('Streamflow')
plt.title(series.site_name)
plt.xticks(rotation='vertical')
# plt.show()
'''