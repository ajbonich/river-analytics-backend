from tbats import TBATS
import numpy as np
import datetime
import matplotlib.pyplot as plt
import sys


def forecast(training_data):

    estimator = TBATS(seasonal_periods=[366],
                      use_arma_errors=False, use_box_cox=False)
    startTime = datetime.datetime.now()
    model = estimator.fit(training_data)

    print('Elapsed Time:', datetime.datetime.now() - startTime)
    print(model.summary())

    return model

    # plt.plot(df, color='darkgreen', label='Training Data')
    # plt.plot(test.index, y_forecast, color='orange', label='Predicted Flow')
    # plt.plot(test.index, test, color='blue', label='Expected Flow')
    # plt.show()


if __name__ == '__main__':
    forecast(sys.argv[1])
