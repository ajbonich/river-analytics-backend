import pandas as pd

bad_request = {
    "status_code": 400,
    "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True,
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET",
    },
    "body": "Bad parameters passed.",
}


def format_output(
    status_code: int, error_message: str, data: pd.DataFrame = None
) -> dict:
    """Creates json dictionary with value label on value objects"""
    body = (
        error_message if data is None else data.reset_index().to_json(orient="records")
    )
    response = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": body,
    }

    return response


def get_forecast(event: dict, object: object) -> dict:
    """Takes in a usgs site id, forecast model, and number of days and returns a list
    of forecast values and 80% confidence interval for the given number of days"""

    try:
        site_id = event["pathParameters"]["siteId"]
        model2 = event.get("modelType", "other model")
        model_type = event["pathParameters"]["modelType"]
        number_of_days = event["queryStringParameters"]["days"]
    except Exception:
        return format_output(400, "Bad inputs")

    return format_output(
        200,
        f"site_id: {site_id} model_type: {model_type} model2: {model2}"
        + f"number_of_days: {number_of_days}",
    )
