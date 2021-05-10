import pandas as pd


def format_output(
    status_code: int = 200, error_message: str = None, data: pd.DataFrame = None
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
