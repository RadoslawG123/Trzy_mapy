import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

plt.style.use('default')
# plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams.update({'figure.figsize': (24, 12), 'figure.dpi': 150})
base_temperatures = pd.read_json('json/temperature_modis.json')
base_temperatures.sort_index(inplace=True)
temperatures = base_temperatures.copy()
y = base_temperatures['lst_day']

print(y)
ax = y.plot()
y.plot()
# plt.xlabel('')
# plt.ylabel('')
ax.set_xlabel('Date', fontsize=14)  # xlabel
ax.set_ylabel('Temperature [K]', fontsize=14)  # ylabel

plt.title('Czernichow temperatures observe with NASA-MODIS', fontsize=16)
plt.tight_layout()
plt.show()

# Define the p, d and q parameters to take any value between 0 and 2
p = d = q = range(0, 2)

# Generate all different combinations of p, q and q triplets
pdq = list(itertools.product(p, d, q))

# Generate all different combinations of seasonal p, q and q triplets
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

# warnings.filterwarnings("ignore") # specify to ignore warning messages
#
# for param in pdq:
#     for param_seasonal in seasonal_pdq:
#         try:
#             mod = sm.tsa.statespace.SARIMAX(y,
#                                             order=param,
#                                             seasonal_order=param_seasonal,
#                                             enforce_stationarity=False,
#                                             enforce_invertibility=False)
#
#             results = mod.fit()
#
#             print(f'ARIMA{param}x{param_seasonal}12 - AIC:{results.aic}')
#         except:
#             continue


# ARIMA(0, 0, 0)x(0, 0, 0, 12)12 - AIC:3201.8629465976464
# ARIMA(0, 0, 0)x(0, 0, 1, 12)12 - AIC:2782.6588927220246
# ARIMA(0, 0, 0)x(0, 1, 0, 12)12 - AIC:1220.9140739136342
# ARIMA(0, 0, 0)x(0, 1, 1, 12)12 - AIC:1050.526009886754
# ARIMA(0, 0, 0)x(1, 0, 0, 12)12 - AIC:1230.8509120445779
# ARIMA(0, 0, 0)x(1, 0, 1, 12)12 - AIC:1125.642077433169
# ARIMA(0, 0, 0)x(1, 1, 0, 12)12 - AIC:1106.7695396494487
# ARIMA(0, 0, 0)x(1, 1, 1, 12)12 - AIC:1052.507199345724
# ARIMA(0, 0, 1)x(0, 0, 0, 12)12 - AIC:2885.3676188590753
# ARIMA(0, 0, 1)x(0, 0, 1, 12)12 - AIC:2484.8085751557755
# ARIMA(0, 0, 1)x(0, 1, 0, 12)12 - AIC:1210.8408048734154
# ARIMA(0, 0, 1)x(0, 1, 1, 12)12 - AIC:1035.0714624865464
# ARIMA(0, 0, 1)x(1, 0, 0, 12)12 - AIC:1235.6836638865395
# ARIMA(0, 0, 1)x(1, 0, 1, 12)12 - AIC:1110.3122684863765
# ARIMA(0, 0, 1)x(1, 1, 0, 12)12 - AIC:1099.5832403397053
# ARIMA(0, 0, 1)x(1, 1, 1, 12)12 - AIC:1037.067945784947
# ARIMA(0, 1, 0)x(0, 0, 0, 12)12 - AIC:1514.258665984748
# ARIMA(0, 1, 0)x(0, 0, 1, 12)12 - AIC:1360.0476831800656
# ARIMA(0, 1, 0)x(0, 1, 0, 12)12 - AIC:1318.3927985414457
# ARIMA(0, 1, 0)x(0, 1, 1, 12)12 - AIC:1130.8795409469017
# ARIMA(0, 1, 0)x(1, 0, 0, 12)12 - AIC:1294.3177554160643
# ARIMA(0, 1, 0)x(1, 0, 1, 12)12 - AIC:1214.2312302221046
# ARIMA(0, 1, 0)x(1, 1, 0, 12)12 - AIC:1191.5580023223788
# ARIMA(0, 1, 0)x(1, 1, 1, 12)12 - AIC:1132.879317615172
# ARIMA(0, 1, 1)x(0, 0, 0, 12)12 - AIC:1467.9076408077924
# ARIMA(0, 1, 1)x(0, 0, 1, 12)12 - AIC:1350.69430213722
# ARIMA(0, 1, 1)x(0, 1, 0, 12)12 - AIC:1219.2732361280048
# ARIMA(0, 1, 1)x(0, 1, 1, 12)12 - AIC:1039.766765715358
# ARIMA(0, 1, 1)x(1, 0, 0, 12)12 - AIC:1227.0770260153392
# ARIMA(0, 1, 1)x(1, 0, 1, 12)12 - AIC:1117.909302472061
# ARIMA(0, 1, 1)x(1, 1, 0, 12)12 - AIC:1109.2700131095835
# ARIMA(0, 1, 1)x(1, 1, 1, 12)12 - AIC:1041.760171420338
# ARIMA(1, 0, 0)x(0, 0, 0, 12)12 - AIC:1521.9443594231557
# ARIMA(1, 0, 0)x(0, 0, 1, 12)12 - AIC:1368.4308794535104
# ARIMA(1, 0, 0)x(0, 1, 0, 12)12 - AIC:1214.9416785867966
# ARIMA(1, 0, 0)x(0, 1, 1, 12)12 - AIC:1040.5738793043843
# ARIMA(1, 0, 0)x(1, 0, 0, 12)12 - AIC:1216.937343149922
# ARIMA(1, 0, 0)x(1, 0, 1, 12)12 - AIC:1114.1542951486786
# ARIMA(1, 0, 0)x(1, 1, 0, 12)12 - AIC:1094.3140680693832
# ARIMA(1, 0, 0)x(1, 1, 1, 12)12 - AIC:1042.5514996583754
# ARIMA(1, 0, 1)x(0, 0, 0, 12)12 - AIC:1480.6985037446805
# ARIMA(1, 0, 1)x(0, 0, 1, 12)12 - AIC:1360.1002444340427
# ARIMA(1, 0, 1)x(0, 1, 0, 12)12 - AIC:1211.7945923895875
# ARIMA(1, 0, 1)x(0, 1, 1, 12)12 - AIC:1034.7560123246526
# ARIMA(1, 0, 1)x(1, 0, 0, 12)12 - AIC:1219.2633715033462
# ARIMA(1, 0, 1)x(1, 0, 1, 12)12 - AIC:1111.4351653192261
# ARIMA(1, 0, 1)x(1, 1, 0, 12)12 - AIC:1096.1971225166442
# ARIMA(1, 0, 1)x(1, 1, 1, 12)12 - AIC:1036.7321521572826
# ARIMA(1, 1, 0)x(0, 0, 0, 12)12 - AIC:1467.1834268136397
# ARIMA(1, 1, 0)x(0, 0, 1, 12)12 - AIC:1355.4832926415427
# ARIMA(1, 1, 0)x(0, 1, 0, 12)12 - AIC:1278.6891769825156
# ARIMA(1, 1, 0)x(0, 1, 1, 12)12 - AIC:1093.0231140163448
# ARIMA(1, 1, 0)x(1, 0, 0, 12)12 - AIC:1264.36362372765
# ARIMA(1, 1, 0)x(1, 0, 1, 12)12 - AIC:1172.5278685966223
# ARIMA(1, 1, 0)x(1, 1, 0, 12)12 - AIC:1150.5971927189798
# ARIMA(1, 1, 0)x(1, 1, 1, 12)12 - AIC:1095.0231129425729
# ARIMA(1, 1, 1)x(0, 0, 0, 12)12 - AIC:1456.9489266400058
# ARIMA(1, 1, 1)x(0, 0, 1, 12)12 - AIC:1350.0523629652166
# ARIMA(1, 1, 1)x(0, 1, 0, 12)12 - AIC:1212.6531536796128
# ARIMA(1, 1, 1)x(0, 1, 1, 12)12 - AIC:1032.1450443058748
# ARIMA(1, 1, 1)x(1, 0, 0, 12)12 - AIC:1209.799125208915
# ARIMA(1, 1, 1)x(1, 0, 1, 12)12 - AIC:1110.9218711955143
# ARIMA(1, 1, 1)x(1, 1, 0, 12)12 - AIC:1094.1198312519903
# ARIMA(1, 1, 1)x(1, 1, 1, 12)12 - AIC:1034.089873255466

# Najmniejsze AIC
# ARIMA(1, 1, 1)x(0, 1, 1, 12)12 - AIC:1032.1450443058748

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 1, 1),
                                seasonal_order=(0, 1, 1, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

fcast = results.get_forecast(4)
print('Forecast:')
print(fcast.predicted_mean)
print('Confidence intervals:')
print(fcast.conf_int())
# https://github.com/statsmodels/statsmodels/issues/4806

print(results.summary().tables[1])

# results.plot_diagnostics(figsize=(15, 12))
fig = plt.figure(figsize=(15, 12), dpi=300)
fig = results.plot_diagnostics(variable=0, lags=10)

# plt.title('Czernichow temperatures observe with NASA-MODIS', fontsize = 16)
plt.tight_layout()

plt.show()

pred = results.get_prediction(start=pd.to_datetime('2017-01-01'), dynamic=False)
pred_ci = pred.conf_int()

ax = y['2000':].plot(label='observed', figsize=(20, 12))
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)
# fcast.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)

ax.set_xlabel('Date', fontsize=14)  # xlabel
ax.set_ylabel('Temperature [K]', fontsize=14)  # ylabel

plt.title('One-step ahead Forecast', fontsize=16)

ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

ax.set_xlabel('Date')
ax.set_ylabel('Temperature [K]')
plt.legend()

plt.show()

y_forecasted = pred.predicted_mean
y_truth = y['2000-02-01':]

# Compute the mean square error
mse = ((y_forecasted - y_truth) ** 2).mean()
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))

pred_dynamic = results.get_prediction(start=pd.to_datetime('2017-01-01'), dynamic=True, full_results=True)
pred_dynamic_ci = pred_dynamic.conf_int()
# print(pred_dynamic.predicted_mean)
# print(pred_dynamic.conf_int())
fig, ax = plt.subplots()

ax = y['2000':].plot(label='Observed', figsize=(20, 15))
pred_dynamic.predicted_mean.plot(label='Dynamic Forecast', ax=ax)

ax.fill_between(pred_dynamic_ci.index,
                pred_dynamic_ci.iloc[:, 0],
                pred_dynamic_ci.iloc[:, 1], color='k', alpha=.25)

ax.fill_betweenx(ax.get_ylim(), pd.to_datetime('2015-01-01'), y.index[-1],
                 alpha=.1, zorder=-1)

ax.set(xlabel='Date', ylabel='Temp', title='SARIMAX Dynamic')
# ax.set_axis_bgcolor("white")
# ax.get_ticklines()
ax.grid(True)

plt.legend()
fig.tight_layout()
plt.show()



y_train = y['2000-02-01':'2017-01-01']


model = sm.tsa.statespace.SARIMAX(y_train,
                                  order=(1, 1, 1),
                                  seasonal_order=(0, 1, 1, 12),
                                  enforce_stationarity=False,
                                  enforce_invertibility=False)

res = model.fit()

fcast = res.get_forecast(12)
print('Forecast:')
print(fcast.predicted_mean)
print('Confidence intervals:')
print(fcast.conf_int())
print(f'y_train o dlugosci {len(y_train)}:')
# print(y_train.lst_day)

fig, ax = plt.subplots()
ax.plot(fcast.predicted_mean)
ax.plot(y_truth['2017-02-01':'2018-01-01'])
plt.show()