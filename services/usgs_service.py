import datetime
import json
import numpy as np
import pandas as pd
import urllib3

defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2100, 12, 31)
defaultParameter = "00060"  # cubic feet per second (cfs)


def get_daily_average_data(
    siteId: str,
    startDate: datetime.date = defaultStartDate,
    endDate: datetime.date = defaultEndDate,
    gaugeParameter: str = defaultParameter,
) -> pd.DataFrame:
    """Calls USGS api to get daily average values in the given date range"""

    url = f"http://waterservices.usgs.gov/nwis/dv/?format=json&site={siteId}&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}"  # noqa: E501
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    responseJson = json.loads(response.data.decode("utf-8"))
    # may have to change this if the json format is different
    return responseJson["value"]["timeSeries"][0]["values"][0]["value"]


def clean_USGS_data(jsonData: dict) -> pd.DataFrame:
    """Given json data, cleans the data and returns a DatFrame"""

    df = pd.DataFrame(jsonData)
    df = df.drop("qualifiers", axis=1)
    df["value"] = df["value"].astype(float)
    df["dateTime"] = pd.to_datetime(df["dateTime"])
    df[df["value"] <= 0] = np.nan
    df = df.ffill()
    df = df.bfill()
    df.set_index("dateTime", inplace=True)

    return df
