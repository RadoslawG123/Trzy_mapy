
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("darkgrid")

sns.set_style("darkgrid")

base_temperatures = pd.read_json('json/temperature_modis.json')
base_temperatures.sort_index(inplace=True)
temperatures = base_temperatures.copy()
print(base_temperatures.head())

temperatures['month'] = temperatures.index.month
temperatures['year'] = temperatures.index.year
print(temperatures.head())


def celsius(k):
    c = k - 273.15
    return c


t_day = temperatures.pivot("month", "year", "lst_day")
t_day = t_day.apply(lambda x: celsius(x))
t_night = temperatures.pivot("month", "year", "lst_night")
t_night = t_night.apply(lambda x: celsius(x))

plt.figure(figsize=(24, 12))
plt.xticks(rotation=90)

# f1, (ax_day, ax_night) = plt.subplots(nrows=1, ncols=2, figsize=(21, 8), dpi=200)
f1, (ax_day, ax_night) = plt.subplots(nrows=1, ncols=2, dpi=150)
# plt.xticks(rotation='vertical')
sns.heatmap(t_day, linewidths=.5, ax=ax_day, cbar_kws={'label': 'Temperature in Celsius'})
ax_day.set_title('Mean daily temperatures', fontsize=14)
ax_day.set_xlabel('Year', fontsize=14)
ax_day.set_ylabel('Month', fontsize=14)
# plt.xticks(rotation='vertical')
sns.heatmap(t_night, linewidths=.5, ax=ax_night, cbar_kws={'label': 'Temperature in Celsius'})
ax_night.set_title('Mean night temperatures', fontsize=14)
ax_night.set_xlabel('Year', fontsize=14)
ax_night.set_ylabel('Month', fontsize=14)
plt.show()

t_day_means = t_day[[2000, 2001, 2002, 2003, 2004]].mean(axis=1, skipna=True)
t_night_means = t_night[[2000, 2001, 2002, 2003, 2004]].mean(axis=1, skipna=True)

t_day_normalized = t_day.subtract(t_day_means, axis=0)
t_night_normalized = t_night.subtract(t_night_means, axis=0)

plt.figure(figsize=(24, 12))
plt.xticks(rotation=90)

f1, (ax_day, ax_night) = plt.subplots(nrows=1, ncols=2, dpi=150)
sns.heatmap(t_day_normalized, linewidths=.5, ax=ax_day, cmap="coolwarm", cbar_kws={'label': 'Temperature in Celsius'})
ax_day.set_title('Normalized temperature index (day)', fontsize=14)
ax_day.set_xlabel('Year', fontsize=14)
ax_day.set_ylabel('Month', fontsize=14)
sns.heatmap(t_night_normalized, linewidths=.5, ax=ax_night, cmap="coolwarm", cbar_kws={'label': 'Temperature in Celsius'})
ax_night.set_title('Normalized temperature index (night)',fontsize=14)
ax_night.set_xlabel('Year', fontsize=14)
ax_night.set_ylabel('Month', fontsize=14)
plt.show()

temp_series = temperatures.melt(id_vars=['year'], value_vars=['lst_day', 'lst_night'])
plt.figure(figsize=(20, 10))
ax_boxplot = sns.boxplot(data = temp_series,
                        x = 'year',
                        y = 'value',
                        hue = 'variable',
                        palette = ['red', 'blue'])
plt.show()

plt.figure(figsize=(20, 10))
ax_lineplot = sns.lineplot(data = temp_series,
                           x = 'year',
                           y = 'value',
                           hue = 'variable',
                           palette = ['red', 'blue'])
plt.show()

def trend(time_series, order=1):
    coeffs = np.polyfit(time_series.index.values, list(time_series), order)
    slope = coeffs[0]
    return float(slope)

series_day = temp_series[temp_series.variable == 'lst_day'].groupby(by='year')['value'].mean()
series_night = temp_series[temp_series.variable == 'lst_night'].groupby(by='year')['value'].mean()

day_trend = trend(series_day)
night_trend = trend(series_night)

print(day_trend, night_trend)

t_day_dropped = t_day.drop([1, 8, 9, 10, 11, 12])
f, ax = plt.subplots(figsize=(10, 10))
sns.heatmap(t_day_dropped, annot=True, linewidths=.5, ax=ax, cmap="coolwarm")
ax.set_title('Mean daily temperatures from February to July')
plt.show()



series_day_dropped = t_day_dropped.mean()
t_night_dropped = t_night.drop([1, 8, 9, 10, 11, 12])
series_night_dropped = t_night_dropped.mean()
print(trend(series_day_dropped), trend(series_night_dropped))


interpolated_day = t_day.interpolate(axis=1, limit_direction='both')
interpolated_night = t_night.interpolate(axis=1, limit_direction='both')
f1, (ax_day, ax_night) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
sns.heatmap(interpolated_day, linewidths=.5, ax=ax_day)
ax_day.set_title('Interpolated mean daily temperatures')
sns.heatmap(interpolated_night, linewidths=.5, ax=ax_night)
ax_night.set_title('Interpolated mean night temperatures')
plt.show()

series_day_interpolated = interpolated_day.mean()
series_night_interpolated = interpolated_night.mean()
print(trend(series_day_interpolated), trend(series_night_interpolated))

print('Trend of the base dataset:\nDay: {},\nNight: {}'.format(day_trend, night_trend))
print('\n')
print('Trend of the months between February and July:\nDay: {},\nNight: {}'.format(
    trend(series_day_dropped),
    trend(series_night_dropped))
     )
print('\n')
print('Trend of the interpolated dataset:\nDay: {},\nNight: {}'.format(
    trend(series_day_interpolated),
    trend(series_night_interpolated))
     )

iday = interpolated_day.reset_index()
iday_melted = iday.melt(id_vars='month', var_name='year', value_name='vals')
iday_melted['year'] = pd.to_numeric(iday_melted['year'])

f, ax = plt.subplots(figsize=(14, 9))
sns.lineplot(x='month', y='vals', hue='year', data=iday_melted,
             palette='BrBG', legend='full')
ax.set_title('Seasonal plot of mean temperatures for a given month')
plt.show()
