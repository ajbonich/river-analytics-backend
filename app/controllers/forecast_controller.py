from app.helpers import controller_helper as helper
from app.services import model_service as service


success_code = 200
error_code = 401


def get_forecast(event: dict, object: object) -> dict:
    """Takes in a usgs site id, forecast model, and number of days and returns a list
    of forecast values and 80% confidence interval for the given number of days"""

    try:
        site_id = event["pathParameters"]["siteId"]
        model_type = event["pathParameters"]["modelType"]
        number_of_days = event["queryStringParameters"]["days"]
    except Exception:
        return helper.format_output(400, "Bad inputs")

    if model_type == "holtwinters":
        forecast = service.generate_holt_winters_forecast(site_id, number_of_days)
        return helper.format_output(success_code, data=forecast)

    if model_type == "fbprophet":
        forecast = service.generate_fbprophet_forecast(site_id, number_of_days)
        return helper.format_output(success_code, data=forecast)

    if model_type == "pystantest":
        import os

        os.system("gcc --version")
        os.system("which gcc")
        test_result = "default_result"
        try:
            test_result = service.test_pystan()
        except Exception as ex:
            print("Error: ")
            print(ex)
            print("Got ENOSPC! Check out df output:\n")
            os.system("df -h")
            exec('du -h / 2>&1 | grep -v "Permission denied"')

        return helper.format_output(200, test_result)

    return helper.format_output(
        error_code, f"'{model_type}' is not a valid model type."
    )
