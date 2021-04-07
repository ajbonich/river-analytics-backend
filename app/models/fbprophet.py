import pandas as pd
from prophet import Prophet
from datetime import datetime


def generate_forecast(df: pd.DataFrame, length: int) -> pd.DataFrame:
    """Takes in a training set (data - value) and a length to
    return a forecast DataFrame"""

    model = Prophet(interval_width=0.50)
    model.fit(df)

    return model.predict(model.make_future_dataframe(periods=length))


def clean_forecast(df: pd.DataFrame) -> pd.DatFrame:
    """Takes in a forecast df and strips unneeded info"""

    today = datetime.today()
    df = df[["ds", "yhat", "yhat_lower", "yhat_upper"]]  # keep important columns
    df = df[(df["ds"] >= today) & (df["ds"] < str(today.year + 1))]  # filter dates
    df["index"] = [date.strftime("%m/%d") for date in df["ds"]]  # add formatted dates
    df = df.drop("ds", axis=1)  # drop old dates
    return df
