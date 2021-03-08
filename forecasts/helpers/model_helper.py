from matplotlib import pyplot as plt

# from sklearn.metrics import (
#     mean_squared_error,
#     mean_absolute_error,
#     mean_absolute_percentage_error,
# )
import datetime
import json
import numpy as np
import os
import pandas as pd
import time
import urllib3

# default data
defaultUseTestData = False
defaultSiteId = "06719505"  # Clear Creek at Golden
defaultStartDate = datetime.date(1888, 1, 1)
defaultEndDate = datetime.date(2100, 12, 31)
defaultParameter = "00060"  # cubic feet per second (cfs)


def getUSGSData(
    useTestData: bool = defaultUseTestData,
    siteId: str = defaultSiteId,
    startDate: datetime.date = defaultStartDate,
    endDate: datetime.date = defaultEndDate,
    gaugeParameter: str = defaultParameter,
) -> pd.DataFrame:
    """Call USGS or get test data"""

    if useTestData:
        with open("testFile.json") as tf:
            print("Using test data.")
            return json.load(tf)

    url = f"http://waterservices.usgs.gov/nwis/dv/?format=json&site={siteId}&startDT={startDate}&endDT={endDate}&parameterCd={gaugeParameter}"  # noqa: E501
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    responseJson = json.loads(response.data.decode("utf-8"))
    # may have to change this if the json format is different
    valueData = responseJson["value"]["timeSeries"][0]["values"][0]["value"]

    return valueData


def create_golden_data_csv():
    """Populates goldenUSGSData.csv with data from USGS"""
    jsonData = getUSGSData()
    df = pd.DataFrame(jsonData)
    df = df.drop("qualifiers", axis=1)
    df["value"] = df["value"].astype(float)
    df["dateTime"] = pd.to_datetime(df["dateTime"])
    df[df["value"] <= 0] = np.nan
    df = df.ffill()
    df = df.bfill()
    df.set_index("dateTime", inplace=True)
    # df.to_csv("./test_data/goldenUSGSData.csv")
    return df


def load_train_test_data(
    trainStart: str,
    trainEnd: str,
    testStart: str,
    testEnd: str,
    from_file: bool = False,
) -> list:
    """Returns a train DataFrame and a test DataFrame"""
    if from_file:
        data = pd.read_csv("app/forecast_data/test_data/goldenUSGSData.csv")
    else:
        data = create_golden_data_csv()
    return data[trainStart:trainEnd], data[testStart:testEnd]  # type: ignore


def plot_train_test_forecast(
    train: pd.DataFrame, test: pd.DataFrame, forecast_lists: list
) -> plt:
    fig, axs = plt.subplots(len(forecast_lists))

    for i in range(len(forecast_lists)):
        # axs[i].plot(train.loc["2015-11-01":], color="darkgreen", label="Training Data"
        # )
        axs[i].plot(test[i].index, test[i], color="blue", label="Expected Flow")
        axs[i].plot(
            test[i].index, forecast_lists[i], color="orange", label="Predicted Flow"
        )
    return plt


def write_simple_results_to_file(results: list) -> None:
    current_time = time.strftime("%b-%d-%y_%H-%M-%S", time.localtime())
    with open(f"{current_time}", "w") as f:
        for result in results:
            f.write(f"{result}\n")


def create_run_directory():
    current_time = time.strftime("%b-%d-%y_%H-%M-%S", time.localtime())
    results_directory = f"./run_results/{current_time}"
    if not os.path.exists(results_directory):
        os.makedirs(results_directory)
    return results_directory
