from statsmodels.graphics.tsaplots import plot_acf  # , plot_pacf
from pandas.plotting import autocorrelation_plot
import matplotlib.pyplot as plt
import pandas as pd


def show_seasonality(df):
    plt.rcParams.update({"figure.figsize": (9, 5)})
    autocorrelation_plot(df.value.tolist())
    plt.show()


def calculate_acf_pacf(df):

    # Calculate ACF and PACF upto 50 lags
    # Original Series
    plt.rcParams.update({"figure.figsize": (9, 7), "figure.dpi": 120})
    # fig,
    fig, axes = plt.subplots(3, 2, sharex=True)
    print(fig)
    axes[0, 0].plot(df.value)
    axes[0, 0].set_title("Original Series")
    plot_acf(df.value, ax=axes[0, 1])

    # 1st Differencing
    axes[1, 0].plot(df.value.diff())
    axes[1, 0].set_title("1st Order Differencing")
    plot_acf(df.value.diff().dropna(), ax=axes[1, 1])

    # 2nd Differencing
    axes[2, 0].plot(df.value.diff().diff())
    axes[2, 0].set_title("2nd Order Differencing")
    plot_acf(df.value.diff().diff().dropna(), ax=axes[2, 1])

    plt.show()


def analyze_stationary(df):

    from statsmodels.tsa.stattools import adfuller

    result = adfuller(df.value)
    print(f"ADF Statistic: {result[0]}")
    print(f"p-value: {result[1]}")
    for key, value in result[4].items():
        print("Critial Values:")
        print(f"   {key}, {value}")


def arima_forecast(df):
    from statsmodels.tsa.arima_model import ARIMA

    # 1,1,2 ARIMA Model
    model = ARIMA(df.value, order=(1, 1, 2))
    model_fit = model.fit(disp=0)
    print(model_fit.summary())


def get_arima_d(train_array):
    from pmdarima.arima import ndiffs

    kpss_diffs = ndiffs(train_array, alpha=0.05, test="kpss", max_d=6)
    adf_diffs = ndiffs(train_array, alpha=0.05, test="adf", max_d=6)
    n_diffs = max(adf_diffs, kpss_diffs)
    print(f"Estimated differencing term: {n_diffs}")
    return n_diffs


def pmdarima_decompose(train):
    from pmdarima import arima
    from pmdarima import utils

    decomposed = arima.decompose(train, "additive", m=12)

    # Plot the decomposed signal of airpassengers as a subplot
    axes = utils.decomposed_plot(
        decomposed, figure_kwargs={"figsize": (6, 6)}, show=False
    )
    return axes


def decompose_data(df):
    # Decomposition
    from statsmodels.tsa.seasonal import seasonal_decompose

    result_mul = seasonal_decompose(
        df["value"], model="multiplicative", extrapolate_trend="freq"
    )
    result_add = seasonal_decompose(
        df["value"], model="additive", extrapolate_trend="freq"
    )
    plt.rcParams.update({"figure.figsize": (10, 10)})
    result_mul.plot().suptitle("Multiplicative Decompose", fontsize=22)
    result_add.plot().suptitle("Additive Decompose", fontsize=22)
    plt.show()

    # Showing the decomp
    df_reconstructed = pd.concat(
        [result_mul.seasonal, result_mul.trend, result_mul.resid, result_mul.observed],
        axis=1,
    )
    df_reconstructed.columns = ["seas", "trend", "resid", "actual_values"]
    df_reconstructed.head()
