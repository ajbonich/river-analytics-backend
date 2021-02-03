from tbats import TBATS, BATS
from statsmodels.tsa.ar_model import AutoReg

import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tools.eval_measures import rmse
# from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import statsmodels.api as sm


def main():
    train, test = get_data()
    model = get_auto_arima_model(train)
    forecasts = model.predict(test.shape[0])
    plot_train_test_forecast(train, test, forecasts)


def get_train_data():

    train = pd.read_csv('trainData.csv')
    train['dateTime'] = pd.to_datetime(train['dateTime'])
    train.set_index('dateTime', inplace=True)
    train = train.asfreq('d')
    train = train.bfill()
    train = train.loc['2018-01-01':]

    return train


def get_test_data():
    test = pd.read_csv('testData.csv')
    test['dateTime'] = pd.to_datetime(test['dateTime'])
    test.set_index('dateTime', inplace=True)

    return test


# def get_tbats_forecast():


def get_auto_arima_model(train):

    import pmdarima as pm
    model = pm.auto_arima(train, start_p=1, start_q=1,
                          test='adf',       # use adftest to find optimal 'd'
                          #   max_p=5, max_q=5, # maximum p and q
                          m=365,              # frequency of series
                          d=1,           # let model determine 'd'
                          seasonal=True,   # No Seasonality
                          start_P=0,
                          D=1,
                          trace=True,
                          suppress_warnings=True,
                          stepwise=True)

    print(model.summary())

    return model


def plot_train_test_forecast(train, test, forecast):
    plt.plot(train, color='darkgreen', label='Training Data')
    plt.plot(test.index, test, color='blue', label='Expected Flow')
    plt.plot(test.index, forecast, color='orange', label='Predicted Flow')
    plt.legend()
    plt.show()
    # Forecast
    # n_periods = 24
    # fitted, confint = sxmodel.predict(n_periods=n_periods,
    #                                   exogenous=np.tile(
    #                                       seasonal_index.value, 2).reshape(-1, 1),
    #                                   return_conf_int=True)

    # index_of_fc = pd.date_range(df.index[-1], periods=n_periods, freq='MS')

    # make series for plotting purpose
    # fitted_series = pd.Series(fitted, index=index_of_fc)
    # lower_series = pd.Series(confint[:, 0], index=index_of_fc)
    # upper_series = pd.Series(confint[:, 1], index=index_of_fc)

    # # Plot
    # plt.plot(df['value'])
    # plt.plot(fitted_series, color='darkgreen')
    # plt.fill_between(lower_series.index,
    #                  lower_series,
    #                  upper_series,
    #                  color='k', alpha=.15)

    # plt.title("SARIMAX Forecast of a10 - Drug Sales")
    # plt.show()


# sm.tsa.seasonal_decompose(df.value).plot()
# result = sm.tsa.stattools.adfuller(df.value)
# plt.show()
'''
y_hat_avg = test.copy()
fit1 = sm(train.value, order=(2, 1, 4), seasonal_order=(0, 1, 1, 7)).fit()
y_hat_avg['SARIMA'] = fit1.predict(
    start="2013-11-1", end="2013-12-31", dynamic=True)
plt.figure(figsize=(16, 8))
plt.plot(train['value'], label='Train')
plt.plot(test['value'], label='Test')
plt.plot(y_hat_avg['SARIMA'], label='SARIMA')
plt.legend(loc='best')
plt.show()

rms = sqrt(mean_squared_error(test.value, y_hat_avg.Holt_Winter))
print(rms)
'''


# # fig, axes = plt.subplots(3, 2, figsize=(12, 16))
# # plt.title('MSFT Autocorrelation plot')

# # # The axis coordinates for the plots
# # ax_idcs = [
# #     (0, 0),
# #     (0, 1),
# #     (1, 0),
# #     (1, 1),
# #     (2, 0),
# #     (2, 1)
# # ]
# # from pandas.plotting import lag_plot
# # for lag, ax_coords in enumerate(ax_idcs, 1):
# #     ax_row, ax_col = ax_coords
# #     axis = axes[ax_row][ax_col]
# #     lag_plot(df['value'], lag=lag, ax=axis)
# #     axis.set_title(f"Lag={lag}")

# # plt.show()


# auto = pm.auto_arima(y_train, d=0, seasonal=False, stepwise=True,
#                  suppress_warnings=True, error_action="ignore", max_p=6,
#                  max_order=None, trace=True)


# fig, axes = plt.subplots(2, 1, figsize=(12, 12))

# # --------------------- Actual vs. Predicted --------------------------
# axes[0].plot(y_train, color='blue', label='Training Data')
# axes[0].plot(test_data.index, forecasts, color='green', marker='o',
#             label='Predicted Price')

# axes[0].plot(test_data.index, y_test, color='red', label='Actual Price')
# axes[0].set_title('Microsoft Prices Prediction')
# axes[0].set_xlabel('Dates')
# axes[0].set_ylabel('Prices')

# # axes[0].set_xticks(np.arange(0, 7982, 1300).tolist(), df['Date'][0:7982:1300].tolist())
# axes[0].legend()

# # ------------------ Predicted with confidence intervals ----------------
# axes[1].plot(y_train, color='blue', label='Training Data')
# axes[1].plot(test_data.index, forecasts, color='green',
#             label='Predicted Price')

# axes[1].set_title('Prices Predictions & Confidence Intervals')
# axes[1].set_xlabel('Dates')
# axes[1].set_ylabel('Prices')

# conf_int = np.asarray(confidence_intervals)
# axes[1].fill_between(test_data.index,
#                     conf_int[:, 0], conf_int[:, 1],
#                     alpha=0.9, color='orange',
#                     label="Confidence Intervals")

# # axes[1].set_xticks(np.arange(0, 7982, 1300).tolist(), df['Date'][0:7982:1300].tolist())
# axes[1].legend()
# Fit model

# Summarize fitted model

# Fit the model
# estimator = TBATS(seasonal_periods=[366],
#                 use_arma_errors=False,  # shall try only models without ARMA
#                 use_box_cox=False  # will not use Box-Cox
#                 )
# model = estimator.fit(df.value)
# # Forecast 365 days ahead
# y_forecast = model.forecast(steps=365)
# plt.plot(df.value)
# plt.plot(y_forecast, color='darkgreen')
# plt.show()
