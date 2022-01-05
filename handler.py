from neuralprophet import NeuralProphet
import json
import logging

import pandas as pd


def forecast(event: dict, context: object) -> dict:
    """
    sdf
    """

    try:
        data_location = "https://raw.githubusercontent.com/ourownstory/neuralprophet-data/main/datasets/"  # noqa
        df = pd.read_csv(data_location + "wp_log_peyton_manning.csv")
        m = NeuralProphet()
        metrics = m.fit(df, freq="D")  # noqa
        predicted = m.predict(df)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET",
            },
            "body": json.dumps({predicted.to_json()}),
        }

    except Exception as e:
        logging.error(e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": repr(e)}),
        }
