# flake8: noqa
from app.models import holt_winters as hwes
from app.helpers import model_helper as mh
from statsmodels.tsa.forecasting.theta import ThetaModel as tm
from statsmodels.tsa.statespace.exponential_smoothing import ExponentialSmoothing as es
from statsmodels.tsa.exponential_smoothing.ets import ETSModel as ets


train_start = "1974-10-01"  # "2017-01-01"
train_end_list = ["2020-03-01"]
# train_end_list = [
#     "2020-03-01",
#     "2020-04-15",
#     "2020-05-01",
#     "2020-05-14",
#     "2020-06-01",
#     "2020-06-14",
# ]
test_start = [
    "2020-03-01",
    "2020-04-15",
    "2020-05-01",
    "2020-05-14",
    "2020-06-01",
    "2020-06-14",
]
test_end = "2020-08-01"


def graph_holt_winters():

    data = mh.create_golden_data_csv()
    forecast_list = [0] * len(train_end_list)
    test = [0] * len(train_end_list)
    for i in range(len(train_end_list)):
        train, test[i] = (
            data[train_start : train_end_list[i]],
            data[test_start[i] : test_end],
        )
        # fit model
        # fit_model = hwes.ets_fit_model(train["value"].tolist())
        # model = tm(train["value"].tolist(), period=366)
        t, d, s, b, r = ["add", True, "add", True, True]
        # model = ets(
        #     train["value"].tolist(),
        #     trend=t,
        #     damped_trend=d,
        #     initialization_method="estimated",
        #     seasonal=s,
        #     seasonal_periods=366,
        # )
        model = es(
            train["value"].tolist(),
            trend=t,
            damped_trend=d,
            initialization_method="estimated",
            seasonal=366,
        )
        fit_model = model.fit()

        # forecast
        forecast_list[i] = fit_model.forecast(len(test[i]))

    # graph
    graphs = mh.plot_train_test_forecast(train, test, forecast_list)
    graphs.show()


if __name__ == "__main__":
    graph_holt_winters()
