try:
    import unzip_requirements  # noqa: F401
except ImportError:
    pass

from statsmodels.tsa.holtwinters import ExponentialSmoothing


def ets_fit_model(
    train_data: list, config: list = ["add", True, "add", True, True]
) -> list:
    """Takes in a test data set and parameters and returns a list of predictions"""
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
    return model.fit()
