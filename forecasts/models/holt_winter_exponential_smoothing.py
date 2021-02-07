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
train_end = "2019-04-21"
test_start = "2019-04-21"
test_end = "2019-09-14"


def ets_forecast(train_data: list, config: list, prediction_count: int) -> list:
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
    # minus 1 to make the correct number of predictions
    return model_fit.predict(len(train_data), len(train_data) + prediction_count - 1)


def test_model(train: list, test: list, config: list, number_forecasts: int) -> list:
    predicted: list = []
    training_data = list(train)
    test_data = list(test)
    print(f"Test length: {len(test)}")
    for set_start_index in range(0, len(test), number_forecasts):
        print(f"Current index: {set_start_index}")
        # make next num_forecasts predictions
        predicted.extend(ets_forecast(training_data, config, number_forecasts))
        # extend training data
        training_data.extend(test_data[:number_forecasts])
        # pop num_forecasts from front of test data
        test_data = test_data[number_forecasts:]

    return predicted

    accuracy = helper.compute_model_accuracy(test, predicted)
    print(accuracy)
    return accuracy, predicted
    # return predicted, helper.compute_model_accuracy(test_data, predicted)


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
    best_forecasts = []
    best_RMSE = float("inf")
    results_df = pd.DataFrame(columns=["Model", "Params", "RMSE", "MAPE", "MSE", "MAE"])
    for number_forecasts in number_forecasts_list:
        for combo in combos:
            config = list(combo)
            config = ["add", True, "add", True, True]
            if config[0] is None and config[1] is True:
                print(f"Skipped: {config} due to invalid configuration")
                continue

            print(f"Testing: {config}")
            predictions = test_model(train_list, test_list, config, number_forecasts)
            results_dict = helper.create_result_item(
                model_type, config, test_list, predictions
            )
            results_df = results_df.append(results_dict, ignore_index=True)
            if results_dict["RMSE"] < best_RMSE:
                best_forecasts = predictions
            break
        helper.save_results(
            model_type,
            results_df,
            number_forecasts,
            train_data,
            test_data,
            best_forecasts,
        )


if __name__ == "__main__":
    train_data, test_data = helper.load_train_test_data(
        train_start, train_end, test_start, test_end
    )
    train_list = train_data["value"].tolist()
    test_list = test_data["value"].tolist()
    parameter_grid_search()
