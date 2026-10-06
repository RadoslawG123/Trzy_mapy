import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels as sm
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters

sns.set_style("darkgrid")
# plt.rcParams.update({'figure.figsize': (9, 7), 'figure.dpi': 120})
plt.rcParams.update({'figure.figsize': (24, 20), 'figure.dpi': 150})
register_matplotlib_converters()

base_temperatures = pd.read_json('json/temperature_modis.json')
base_temperatures.sort_index(inplace=True)
temperatures = base_temperatures.copy()
print(base_temperatures.head())
dataDD = base_temperatures['lst_day'].to_dict()
datalst = list(dataDD.values())
df = pd.DataFrame(datalst)
# print(df)

# plt.figure(figsize=(10, 10))
# plt.subplot(211)
# # datalst.hist()
# base_temperatures['lst_day'].hist()
# plt.subplot(212)
# # datalst.plot(kind='kde')
# base_temperatures['lst_day'].plot(kind='kde')
# plt.show()

plt.figure()

# Original Series
fig, axes = plt.subplots(3, 2, sharex=False)
# ax_lineplot = sns.lineplot(data=df)
axes[0, 0].plot(df)
axes[0, 0].set_title('Original Series')
axes[0, 0].set_ylabel('Temperature[K]')
axes[0, 0].set_xlabel('Measurement no.')
plot_acf(df, ax=axes[0, 1])

# 1st Differencing
axes[1, 0].plot(df.diff())
axes[1, 0].set_title('1st Order Differencing')
axes[1, 0].set_ylabel('Temp. diff. [K]')
axes[1, 0].set_xlabel('Measurement no.')
plot_acf(df.diff().dropna(), ax=axes[1, 1])

# 2nd Differencing
axes[2, 0].plot(df.diff().diff())
axes[2, 0].set_title('2nd Order Differencing')
axes[2, 0].set_ylabel('Temp. diff. [K]')
axes[2, 0].set_xlabel('Measurement no.')
plot_acf(df.diff().diff().dropna(), ax=axes[2, 1])

plt.show()

plt.rcParams.update({'figure.figsize': (9, 4), 'figure.dpi': 300})
# PACF plot of 1st differenced series
fig, axes = plt.subplots(1, 2, sharex=False)
axes[0].plot(df.diff());
axes[0].set_title('1st Differencing')
axes[1].set(ylim=(-1, 3))
plot_pacf(df.diff().dropna(), ax=axes[1])

plt.show()

fig, axes = plt.subplots(1, 2, sharex=False)
axes[0].plot(df.diff());
axes[0].set_title('1st Differencing')
axes[1].set(ylim=(-1, 1.2))
plot_acf(df.diff().dropna(), ax=axes[1])

plt.show()

plt.rcParams.update({'figure.figsize': (9, 3), 'figure.dpi': 300})
# PACF plot of 2nd differenced series
fig, axes = plt.subplots(1, 2, sharex=False)
axes[0].plot(df.diff().diff());
axes[0].set_title('2nd Differencing')
axes[1].set(ylim=(-1, 3))
plot_pacf(df.diff().diff().dropna(), ax=axes[1])

plt.show()

fig, axes = plt.subplots(1, 2, sharex=False)
axes[0].plot(df.diff().diff());
axes[0].set_title('2nd Differencing')
axes[1].set(ylim=(-1, 1.2))
plot_acf(df.diff().diff().dropna(), ax=axes[1])

plt.show()


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
# print('Data Check')
# print(lst_day_validation)
# print('###########')
# print(lst_day_train)
#
# model = ARIMA(lst_day_train, order=(1, 1, 0))
# model_fit = model.fit(disp=0)
# print(model_fit.summary())
#
# residuals = pd.DataFrame(model_fit.resid)
# fig, ax = plt.subplots(1, 2)
# residuals.plot(title="Residuals", ax=ax[0])
# residuals.plot(kind='kde', title='Density', ax=ax[1])
# plt.show()
#
# # Actual vs Fitted
# model_fit.plot_predict(dynamic=False)
# plt.show()

# model = ARIMA(lst_day_train, order=(2, 2, 0))
# model_fit = model.fit(disp=0)
# print(model_fit.summary())
#
# residuals = pd.DataFrame(model_fit.resid)
# fig, ax = plt.subplots(1, 2)
# residuals.plot(title="Residuals", ax=ax[0])
# residuals.plot(kind='kde', title='Density', ax=ax[1])
# plt.show()
#
# # Actual vs Fitted
# model_fit.plot_predict(dynamic=False)
# plt.show()


# # Build Model
# print(lst_day_train)
# model = ARIMA(lst_day_train, order=(1, 1, 0)).fit()
# fc, se, conf = model.forecast(len(lst_day_validation), alpha=0.05)
#
# print(len(fc))
# # make Panda series
# fc_series = pd.Series(fc, index=lst_day_validation.index)
# lower_series = pd.Series(conf[:, 0], index=lst_day_validation.index)
# upper_series = pd.Series(conf[:, 1], index=lst_day_validation.index)
#
# plt.figure(figsize=(12, 5), dpi=300)
# plt.plot(lst_day_train, label='training')
# plt.plot(lst_day_validation, label='validation')
# plt.plot(fc_series, label='forecast')
# plt.title('Forecast vs Actuals')
# plt.legend(loc='upper left', fontsize=12)
# plt.show()


# Build Model
print(lst_day_train)
model = ARIMA(base_temperatures['lst_day'], order=(1, 1, 0)).fit()
model.plot_predict(dynamic=False)
plt.figure(figsize=(12, 5), dpi=300)
plt.plot(base_temperatures['lst_day'].diff())
plt.plot(model.fittedvalues, color='red')
plt.show()

predictions_ARIMA_diff = pd.Series(model.fittedvalues, copy=True)
x, x_diff = base_temperatures['lst_day'].iloc[0], predictions_ARIMA_diff.iloc[1:]
predictions_ARIMA = np.r_[x, x_diff].cumsum().astype(float)
print(len(predictions_ARIMA))
print(len(base_temperatures))
predictions = pd.Series(predictions_ARIMA, index=base_temperatures['lst_day'][1:].index)
print(model.fittedvalues.tail())
print(predictions.tail())

plt.figure(figsize=(12, 5), dpi=300)
# plt.plot(base_temperatures['lst_day'])
plt.plot(predictions, color='red', label='Forecast')
plt.plot(lst_day_train, label='Training')
plt.plot(lst_day_validation, label='Validation')
# plt.plot(model.fittedvalues, )
plt.title('Forecast vs Actuals')
plt.legend(loc='upper left', fontsize=12)
plt.show()

# fc, se, conf = model.forecast(15, alpha=0.05)

# print(len(fc))
# make Panda series
# fc_series = pd.Series(fc, index=lst_day_validation.index[len(lst_day_validation)-15:])
# lower_series = pd.Series(conf[:, 0], index=lst_day_validation.index)
# upper_series = pd.Series(conf[:, 1], index=lst_day_validation.index)


# plt.figure(figsize=(12, 5), dpi=300)

# plt.show()
# decomposition = sm.tsa.seasonal.seasonal_decompose(df, model='additive')
# fig = decomposition.plot()
# plt.show()
