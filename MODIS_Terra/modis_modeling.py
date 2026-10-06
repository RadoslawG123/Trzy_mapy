import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters
sns.set_style("darkgrid")


register_matplotlib_converters()

base_temperatures = pd.read_json('json/temperature_modis.json')
base_temperatures.sort_index(inplace=True)
temperatures = base_temperatures.copy()
print(base_temperatures.head())


def prepare_data_for_arima(dataset, training_size=0.8):
    dataset_len = len(dataset)
    print('Dataset has: {} records'.format(
        dataset_len))
    limit = int(training_size * len(dataset))
    training = dataset[:limit]
    validation = dataset[limit:]
    print('Training set has: {} records. Validation set has {} records.'.format(
        len(training), len(validation)))
    return training, validation


lst_day_train, lst_day_validation = prepare_data_for_arima(base_temperatures['lst_day'])


def mean_abs_perc_error(predictions, validation_data):
    mape = np.mean(np.abs(predictions - validation_data) / np.abs(validation_data))
    return mape


def test_walk_forward(train_set, validation_set):
    observation = [train_set[-1]]  # The first predicted value
    predictions = []
    for i in range(len(validation_set)):
        # Prediction
        predictions.append(observation[-1])
        # Observation
        obs = validation_set[i]
        observation.append(obs)
    error_percent = mean_abs_perc_error(predictions, validation_set)
    print(error_percent)
    return error_percent

base_error = test_walk_forward(lst_day_train, lst_day_validation)

# Is time series stationary? (no)

fuller_test = adfuller(lst_day_train)
print('ADF:', fuller_test[0])
print('p-value:', fuller_test[1])
print('critical values:', fuller_test[4])



# Line, ACF, PACF plots of an unchanged signal

fig, axes = plt.subplots(1, 3, sharex=False, figsize=(15, 7))
axes[0].plot(lst_day_train.values)
axes[0].set_title('Base signal')
plot_acf(lst_day_train.values, ax=axes[1])
plot_pacf(lst_day_train.values, ax=axes[2])
plt.show()



# 1st order differentiation

fig, axes = plt.subplots(1, 3, sharex=False, figsize=(15, 7))
axes[0].plot(lst_day_train.diff().values)
axes[0].set_title('Signal differentiated one time')
plot_acf(lst_day_train.diff().dropna().values, ax=axes[1])
plot_pacf(lst_day_train.diff().dropna().values, ax=axes[2])
plt.show()

# 2nd order differentiation

fig, axes = plt.subplots(1, 3, sharex=False, figsize=(15, 7))
axes[0].plot(lst_day_train.diff().diff().values)
axes[0].set_title('Signal differentiated two times')
plot_acf(lst_day_train.diff().diff().dropna().values, ax=axes[1])
plot_pacf(lst_day_train.diff().diff().dropna().values, ax=axes[2])
plt.show()

# Is time series stationary after differentiation? (yes)

fuller_test = adfuller(lst_day_train.diff().dropna().values)
print('ADF:', fuller_test[0])
print('p-value:', fuller_test[1])
print('critical values:', fuller_test[4])
print('')

# Prediction for the model: AR = 1, I = 1, MA = 0 (p,d,q)

model = ARIMA(lst_day_train.values, order=(1, 1, 0))
model_fit = model.fit(trend='nc', disp=0)
print(model_fit.summary())

# Residuals

residuals = pd.DataFrame(model_fit.resid)
fig, ax = plt.subplots(1, 2, sharex=False, figsize=(15, 7))
residuals.plot(title="Residuals", ax=ax[0])
residuals.plot(kind='kde', title='Density', ax=ax[1])
plt.show()



fig, ax = plt.subplots(1, 1, figsize=(15, 7))
model_fit.plot_predict(dynamic=False, ax=ax)
plt.show()


# Model validation

def arima_validation(training_set, validation_set, arima_model, model_order):
    history = list(training_set)

    # first prediction
    predictions = []
    predicted = float(arima_model.forecast()[0])
    predictions.append(predicted)
    history.append(validation_set[0])

    # rolling forecasts
    for i in range(1, len(validation_set)):
        model = ARIMA(history, model_order)
        model_fit = model.fit(trend='nc', disp=0)
        predicted = model_fit.forecast()[0]
        predictions.append(predicted[0])

        # observation
        obs = validation_set[i]
        history.append(obs)
        print('>> Predicted = {:.1f}, Expected = {:.1f}'.format(predicted[0], obs))
    return predictions


forecasts = arima_validation(lst_day_train.values, lst_day_validation.values, model_fit, (1, 1, 0))
error_value = mean_abs_perc_error(forecasts, lst_day_validation.values)

print('Error value is:', error_value)

fig, ax = plt.subplots(1, 1, figsize=(15, 7))
plt.plot(lst_day_validation.index, lst_day_validation.values)
plt.plot(lst_day_validation.index, forecasts)
plt.legend(['True value', 'Predictions'])
plt.show()

# SARIMAX model

model = SARIMAX(lst_day_train.values, order=(1, 1, 0), seasonal_order=(1, 1, 1, 12))
model_fit = model.fit(trend='nc', disp=0)
print(model_fit.summary())

# Residuals

residuals = pd.DataFrame(model_fit.resid)
fig, ax = plt.subplots(1, 2, sharex=False, figsize=(15, 7))
residuals.plot(title="Residuals", ax=ax[0])
residuals.plot(kind='kde', title='Density', ax=ax[1])
plt.show()


# SARIMAX validation

def sarima_validation(training_set, validation_set, sarima_model, model_order, seasonal_order):
    history = list(training_set)

    # first prediction
    predictions = []
    predicted = float(sarima_model.forecast()[0])
    predictions.append(predicted)
    history.append(validation_set[0])

    # rolling forecasts
    for i in range(1, len(validation_set)):
        model = SARIMAX(history, order=model_order, seasonal_order=seasonal_order)
        model_fit = model.fit(trend='nc', disp=0)
        predicted = model_fit.forecast()[0]
        predictions.append(predicted)

        # observation
        obs = validation_set[i]
        history.append(obs)
        print('>> Predicted = {:.1f}, Expected = {:.1f}'.format(predicted, obs))
    return predictions


forecasts = sarima_validation(lst_day_train.values, lst_day_validation.values, model_fit,
                              (1, 1, 0), (1, 1, 1, 12))
error_value = mean_abs_perc_error(forecasts, lst_day_validation.values)

print('Error value is:', error_value)

fig, ax = plt.subplots(1, 1, figsize=(15, 7))
plt.plot(lst_day_validation.index, lst_day_validation.values)
plt.plot(lst_day_validation.index, forecasts)
plt.legend(['True value', 'Predictions'])
plt.show()

def test_walk_forward_by_period(train_set, validation_set, period=12):
    j = -period
    observation = [train_set[j]]  # The first predicted value
    predictions = []
    for i in range(len(validation_set)):
        # Prediction
        predictions.append(observation[-1])
        # Observation
        j = j + 1
        if j < 0:
            obs = train_set[j]
        else:
            obs = validation_set[i-(period-1)]
        observation.append(obs)
    error_percent = mean_abs_perc_error(predictions, validation_set)
    return error_percent



print('>> Seasonal base error is:', test_walk_forward_by_period(lst_day_train, lst_day_validation), '%')












