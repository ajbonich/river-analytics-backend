try:
    import unzip_requirements  # noqa: F401
except ImportError:
    pass

import datetime as dt
import pandas as pd
import pystan

# from app.models import fbprophet as fbp
from app.models import holt_winters as hwes
from app.services import usgs_service

start_date = dt.date(1990, 1, 1)  # only train forecast from data since 1990


def generate_holt_winters_forecast(site_id: str, forecast_length: int) -> pd.DataFrame:
    """Given a site, model, and length, returns a forecast DataFrame"""

    site_data = usgs_service.get_daily_average_data(site_id, start_date)
    clean_data = usgs_service.clean_USGS_data(site_data)
    offset_days = int((dt.datetime.today() - clean_data.tail(1).index).days[0])
    offset_days += int(forecast_length)

    fitted_model = hwes.ets_fit_model(clean_data["value"].tolist())
    forecast_list = fitted_model.forecast(offset_days)
    forecast_dates = pd.date_range(
        clean_data.tail(1).index[0] + dt.timedelta(days=1),
        periods=offset_days,
    )
    formatted_dates = [date.strftime("%m/%d") for date in forecast_dates]

    return pd.DataFrame({"forecast": forecast_list}, index=formatted_dates)


def generate_fbprophet_forecast(site_id: str, forecast_length: int) -> pd.DataFrame:
    """Given a site, model, and length, returns a forecast DataFrame using fbprophet"""

    site_data = usgs_service.get_daily_average_data(site_id)
    clean_data = usgs_service.clean_USGS_data(site_data)
    clean_data.columns = ["ds", "y"]

    return None  # fbp.generate_forecast(clean_data)


def test_pystan() -> float:

    model_code = "parameters {real y;} model {y ~ normal(0,1);}"
    model = pystan.StanModel(model_code=model_code)  # this will take a minute
    y = model.sampling(n_jobs=1).extract()["y"]
    return y.mean()  # should be close to 0
