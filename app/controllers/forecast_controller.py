from app.helpers import controller_helper as helper
from app.services import model_service as service


success_code = 200
error_code = 400


# def get_forecast(event: dict, context: object) -> dict:
#     """Takes in an usgs site id, forecast model, and number of days and returns a list
#     of forecast values and 80% confidence interval for the given number of days.
#     Also returns the actual values before the current calendar day"""
#
#     try:
#         site_id = event["site_id"]
#         # model_type = event["pathParameters"]["modelType"]
#         # number_of_days = event["queryStringParameters"]["days"]
#     except Exception:
#         return helper.format_output(error_code, "Bad inputs")


def get_forecast(site_id: str) -> dict:

    # if model_type == "fbprophet":
    forecast = service.generate_prophet_forecast(site_id)
    return helper.format_output(success_code, data=forecast)

    # return helper.format_output(
    #     error_code, f"'{model_type}' is not a valid model type."
    # )
