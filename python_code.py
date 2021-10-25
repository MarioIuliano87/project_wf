import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Reading the data
path = '/Users/iuliano/Documents/Proj/'
df = pd.read_excel(path + 'Dataset - Case Study - BI Analyst Wunderflats.xlsx')

# Rename columns
df = df.rename(columns={'dteday': 'date',
                        'yr': 'year_sk',
                        'mnth': 'month_int',
                        'hr': 'hour',
                        'weathersit': 'weather_sk',
                        'hum': 'humidity',
                        'season': 'season_sk',
                        'cnt': 'totals'})

# Dataset Exploration
print('Rows: ', df.shape[0])
print('Columns: ', df.shape[1])
print(df.info())
print('Total NULL Values per Columns\n', df.isna().sum())

# Plotting a quick correlation heatmap to have an overall view of relationships among features
corr = df.corr()
sns.heatmap(corr, annot=True)
plt.title('Correlation Heatmap among Features')

# Casual drivers are positively correlated with temperatures, and negativily correlated with humidity.
# This shows that casual drivers are in relation with weather conditions
# For registered drivers, the correlation is weaker showing that they might be more daily commuters

# Time Range #
min_d = df.date.min()
max_d = df.date.max()
print('Min date: ', min_d)
print('Max date: ', max_d)
# 2 Years data

# Totals across time
df['year'] = df['date'].dt.year
totals = df.groupby('year', as_index=False)['totals'].sum()
_ = totals.plot.bar(x='year')
plt.title('Total Rides by Year')

# Total registered and casual rides by year
reg_cas = df.groupby('year', as_index=False)[['registered', 'casual', 'totals']].sum()
_ = reg_cas[['year', 'registered', 'casual']].plot.bar(x='year')
plt.title('Bike usage for Registered and Casual by Year')
plt.ylabel('Count Rides')

reg_cas['registered'] = round((reg_cas['registered'] / reg_cas['totals']) * 100, 0)
reg_cas['casual'] = round((reg_cas['casual'] / reg_cas['totals']) * 100, 0)
print('Yearly Share of Registered and Casual\n', reg_cas)

# The percentage of registered increased by 2 points in 2012 and casual lost 2 points.
# Showing that something has been done to promote registrations over casual and
# that potentially casual have been converted into registered. As we don't have the granularity
# on a single user we cannot estimate how many converted.

# Month trend
df['year_month'] = df['date'].dt.to_period('M')
monthly = df.groupby('year_month', as_index=False)[['registered', 'casual']].sum().plot(x='year_month')
plt.title('Monthly Service Usage by Registared and Casual')
plt.show()

# Seasonal trend: can we observe different trends across seasons?
df['year_season'] = df['year'].astype(str) + '_' + df['season_sk'].astype(str)
seasonal = df.groupby('season_sk', as_index=False)[['registered', 'casual']].sum().plot.bar(x='season_sk')
plt.title('Seasonal Trend by Registered and Casual')

# Srping, Summer and Fall are the seasons with most users
# Distribution of rides across seasons
sns.boxplot(x=df['season_sk'], y='totals', data=df)
plt.title('Distribution of Rides across Seasons')

# Let's have a look at the weekdays and group by reg and cas
df['day_name'] = df.date.dt.day_name()
df['weekday'] = df.weekday.astype(int)
df['day_name'] = df.weekday.astype(str) + df.day_name
week_day = df.groupby('day_name', as_index=False)[['registered', 'casual']].sum().plot.bar(x='day_name')
week_day.plot.bar(x='day_name', y=['registered', 'casual'])

dist_day = df[['day_name', 'registered', 'casual']]
fig, ax = plt.subplots(2, 1)
sns.boxplot(dist_day['day_name'], dist_day['registered'], ax=ax[0])
ax[0].set_title('Weekday Distribution - Registered')
ax[0].set_xlabel("")
sns.boxplot(dist_day['day_name'], dist_day['casual'], ax=ax[1])
ax[1].set_title('Weekday Distribution - Casual')
ax[1].set_xlabel("")

# Hourly rides by reg and cas
df.groupby('hour', as_index=False)[['registered', 'casual']].sum().plot(x='hour')
plt.title('Hourly Trend')
plt.show()

# Hourly trend over the weekend and workingdays
fig, ax = plt.subplots(2, 1)
working_day = df[df.weekday == 1].groupby('hour', as_index=False)[['registered', 'casual']].sum()
weekends = df[df.weekday == 0].groupby('hour', as_index=False)[['registered', 'casual']].sum()
ax[0].plot(working_day['hour'], working_day[['registered', 'casual']], marker='v', linestyle='--')
ax[0].set_title('Hourly Working Days Rides')
ax[1].plot(weekends['hour'], weekends[['registered', 'casual']], marker='v', linestyle='--')
ax[1].set_title('Hourly Weekends Rides')
# Weekdays and weekends have opposite trends. But the increase of casual is remarkable during the weekend

# What's the relationship with the weather?
sns.heatmap(df[['temp', 'windspeed', 'humidity', 'registered', 'casual']].corr(), annot=True)
plt.title('Heatmap of Rides in Correlation with Weather')
# The casual riders seem to be more sensitive to temperature. As it increases, also casual riders are more around.


# Creating 2 dimensional table and joining to use labels instead of sk.

# Create Dim Tables to merge #
dim_season = pd.DataFrame({'season_sk': [1, 2, 3, 4],
                           'season': ['winter', 'spring', 'summer', 'fall']})

dim_weather = pd.DataFrame({'weather_sk': [1, 2, 3, 4],
                            'weather': ['Few clouds, Partly cloudy, Partly cloudy',
                                        'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
                                        'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds',
                                        'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog']})

# Join the 2 tables on sk
data = df.merge(dim_season, how='inner', on='season_sk').merge(dim_weather, how='inner', on='weather_sk')

bike_share = data[
    ['instant', 'date', 'year', 'year_season', 'month_int', 'hour', 'holiday', 'weekday', 'workingday', 'season',
     'weather', 'temp', 'atemp', 'humidity', 'windspeed', 'casual', 'registered', 'totals']]

# Export cleaned data set as csv file and plot it into Tableau
wf = bike_share.to_csv(path + 'bike_sharing_wf.csv',
                       header=True,
                       index=False)
