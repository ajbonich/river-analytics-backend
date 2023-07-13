from app.controllers.forecast_controller import get_forecast
from app.helpers import controller_helper as helper


def handler(event: dict, context: object) -> dict:
    """Takes in an usgs site id, forecast model, and number of days and returns a list
    of forecast values and 80% confidence interval for the given number of days"""

    try:
        site_id = event["site_id"]
        # number_of_days = int(event["queryStringParameters"]["days"])
        # include_history = bool(event["queryStringParameters"]["include_history"])
        # interval_width = float(event["queryStringParameters"]["confidence_width"])
    except Exception:
        return helper.format_output(400, "Bad inputs")

    return get_forecast(site_id)
