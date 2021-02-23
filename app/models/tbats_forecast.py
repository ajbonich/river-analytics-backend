from tbats import TBATS

# import numpy as np
import datetime

# import matplotlib.pyplot as plt
import sys


if __name__ == "__main__":
    estimator = TBATS(seasonal_periods=[365], use_arma_errors=False, use_box_cox=False)
    startTime = datetime.datetime.now()
    model = estimator.fit(sys.argv[1])

    print("Elapsed Time:", datetime.datetime.now() - startTime)

    print(model.summary())

    # plt.plot(df, color='darkgreen', label='Training Data')
    # plt.plot(test.index, y_forecast, color='orange', label='Predicted Flow')
    # plt.plot(test.index, test, color='blue', label='Expected Flow')
    # plt.show()
