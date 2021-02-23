from app.models import holt_winters as hwes
from app.services import usgs_service
import pandas as pd
import datetime as dt


def generate_holt_winters_forecast(site_id: str, forecast_length: int) -> pd.DataFrame:
    """Given a site, model, and length, returns a forecast DataFrame"""

    site_data = usgs_service.get_daily_average_data(site_id)
    clean_data = usgs_service.clean_USGS_data(site_data)
    offset_days = (dt.datetime.today() - clean_data.tail(1).index).days[0]
    total_forecast_length = offset_days + forecast_length

    forecast_list = hwes.ets_forecast(site_data, total_forecast_length)
    forecast_dates = pd.date_range(
        clean_data.tail(1).index[0] + dt.timedelta(days=1),
        periods=total_forecast_length,
    )
    formatted_dates = [date.strftime("%m/%d") for date in forecast_dates]

    return pd.DataFrame({"date": formatted_dates, "forecast": forecast_list})
