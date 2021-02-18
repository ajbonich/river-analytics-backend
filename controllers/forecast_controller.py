from helpers import controller_helper as helper


def get_forecast(event: dict, object: object) -> dict:
    """Takes in a usgs site id, forecast model, and number of days and returns a list
    of forecast values and 80% confidence interval for the given number of days"""

    try:
        site_id = event["pathParameters"]["siteId"]
        model_type = event["pathParameters"]["modelType"]
        number_of_days = event["queryStringParameters"]["days"]
    except Exception:
        return helper.format_output(400, "Bad inputs")

    return helper.format_output(
        200,
        f"site_id: {site_id} model_type: {model_type}"
        + f"number_of_days: {number_of_days}",
    )
