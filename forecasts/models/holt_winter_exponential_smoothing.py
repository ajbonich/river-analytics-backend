from statsmodels.tsa.holtwinters import ExponentialSmoothing
import itertools
from helpers import model_helper as helper
import pandas as pd

# from multiprocessing import cpu_count
# from joblib import Parallel
# from joblib import delayed
# from warnings import catch_warnings
# from warnings import filterwarnings


# If I want to add running models in parallel
# from multiprocessing import cpu_count
# from joblib import Parallel
# from joblib import delayed
# from warnings import catch_warnings
# from warnings import filterwarnings
train_start = "1974-10-01"  # "2017-01-01"
train_end = "2018-05-01"
test_start = "2018-05-01"
test_end = "2018-08-01"


def ets_forecast(train_data: list, config: list, steps: int) -> list:
    """Takes in a test data set and parameters and returns an ETS model"""
    t, d, s, b, r = config
    if s is None:
        model = ExponentialSmoothing(
            train_data,
            trend=t,
            damped_trend=d,
            use_boxcox=b,
            initialization_method="estimated",
        )
    else:
        model = ExponentialSmoothing(
            train_data,
            trend=t,
            damped_trend=d,
            use_boxcox=b,
            initialization_method="estimated",
            seasonal=s,
            seasonal_periods=365,
        )
    model_fit = model.fit()
    return model_fit.forecast(steps)


def test_model(train: list, test: list, config: list, number_forecasts: int) -> list:
    predicted: list = []
    training_data = list(train)
    remaining_test_data = list(test)
    print(f"Test data length: {len(test)}")
    while len(remaining_test_data) > 0:
        # make next num_forecasts predictions
        predicted.extend(
            ets_forecast(
                training_data, config, min(number_forecasts, len(remaining_test_data))
            )
        )
        # extend training data
        training_data.extend(remaining_test_data[:number_forecasts])
        # pop num_forecasts from front of test data
        remaining_test_data = remaining_test_data[number_forecasts:]

    return predicted


def parameter_grid_search():
    """Takes in test data and returns the accuracy result of using different parameters:
    trend, damped, seasonal, seasonal_periods, remove_bias parameters"""
    t_params = ["add", "mul", None]
    d_params = [True, False]
    s_params = ["add", "mul"]  # [None]  # [None, "add", "mul"]
    b_params = [True, False]
    r_params = [True, False]
    combos = list(itertools.product(t_params, d_params, s_params, b_params, r_params))
    print(f"{len(combos)} sets of parameters generated")

    number_forecasts_list = [7, 14, 30, 60, 90]
    model_type = "ETS"
    results_df = pd.DataFrame(
        columns=["RMSE", "MAPE", "MSE", "MAE", "Model", "Steps", "Params"]
    )
    results_directory = helper.create_run_directory()
    number_forecasts_list = [1]
    for steps in number_forecasts_list:
        for combo in combos:
            config = list(combo)
            config = ["add", True, "add", True, True]
            if config[0] is None and config[1] is True:
                print(f"Skipped: {config} due to invalid configuration")
                continue

            print(f"Testing: {config}")
            predictions = test_model(train_list, test_list, config, steps)

            figure = helper.plot_train_test_forecast(train_data, test_data, predictions)
            figure.savefig(f"{results_directory}/{steps}_forecast_steps.png")
            figure.clf()

            result = helper.compute_model_accuracy(test_list, predictions)
            result.update({"Model": model_type, "Steps": steps, "Params": config})
            results_df = results_df.append(result, ignore_index=True)
            break

    results_df.to_csv(f"{results_directory}/Performance")


if __name__ == "__main__":
    train_data, test_data = helper.load_train_test_data(
        train_start, train_end, test_start, test_end
    )
    train_list = train_data["value"].tolist()
    test_list = test_data["value"].tolist()
    parameter_grid_search()
