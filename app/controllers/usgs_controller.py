import datetime
import pandas as pd

from app.helpers import controller_helper as helper
from app.services import usgs_service

# TODO: make a call to get the period data is available

# default data
default_site_id = "06719505"  # Clear Creek at Golden
default_start_date = datetime.date(1888, 1, 1)
default_end_date = datetime.date(2100, 12, 31)
default_parameter = "00060"  # cubic feet per second (cfs)
default_min_flow = 300
default_max_flow = 1000


def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, PUT, DELETE, OPTIONS"
    return response


def get_daily_average_data(event, object):
    """Makes a usgs call with given or default parameters
    to create a clean dataframe object"""
    try:
        site_id = event["queryStringParameters"]["site_id"]
    except Exception:
        site_id = default_site_id

    try:
        start_date = event["queryStringParameters"]["start_date"]
    except Exception:
        start_date = default_start_date

    try:
        end_date = event["queryStringParameters"]["end_date"]
    except Exception:
        end_date = default_end_date
    try:
        parameter = event["queryStringParameters"]["gaugeParameter"]
    except Exception:
        parameter = default_parameter

    data = usgs_service.get_usgs_data(site_id, start_date, end_date, parameter)
    clean_data = usgs_service.format_season_average_data(data)
    return_data = pd.DataFrame(clean_data.mean(axis=1).astype(int), columns=["average"])
    return_data["middleFifty"] = list(
        zip(
            clean_data.quantile(0.25, axis=1).astype(int),
            clean_data.quantile(0.75, axis=1).astype(int),
        )
    )
    return helper.format_output(data=return_data)


def get_daily_runnable_percentage(event, object):
    """Takes in a mimimum and maximum value for the section and returns
    a graph displaying the odds the section is runnable for each day
    """

    try:
        site_id = event["queryStringParameters"]["site_id"]
    except Exception:
        site_id = default_site_id

    try:
        min_flow = int(event["queryStringParameters"]["min_flow"])
    except Exception:
        min_flow = default_min_flow

    try:
        max_flow = int(event["queryStringParameters"]["max_flow"])
    except Exception:
        max_flow = default_max_flow

    data = usgs_service.get_daily_average_data(site_id)
    average_data = usgs_service.format_season_average_data(data)

    count_in_range = average_data[
        (average_data > min_flow) & (average_data < max_flow)
    ].count(axis=1)
    total_count = average_data[average_data > 0].count(axis=1)
    daily_percent = pd.DataFrame()
    daily_percent["percent"] = count_in_range.div(total_count)
    # daysOver50 = percentages[percentages > 50]

    return helper.format_output(daily_percent * 100)
