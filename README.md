# Wunderflat Case Study # 

## Objective ##

The goal of this analysis is to identify a key finding(s) from the data that would help drive
more revenue to the business. 

## Approach ## 

1. Business Understanding
2. High level exploration in Python 
3. Visualisations in Tableau
4. Insights

Note: the analysis has been conducted entirely in Python and results plotted into Tableau. No SQL has been usued during the analysis. 
 
 ## Business Understanding ## 
 
 Now we have the data. 
 
 How can I support the businees towards generating more revenue? 
 
 Simple question: How do bike shares programs generate revenue? 
 
 - Memebership plan (annual fee) 
 - Pay-as-you-go plan
 
The pay-as-you-go plan might be consumed by customers who occasionally commute within the city or bus/train/car drivers who tend to prefer other transports. 

Although increasing casual commuters will still represent a source of revenue, the most significant growth comes from long-term consumers.

**I will use the data to explore opportunities to identify opportunities to attract more customers to the bike service**

## High level exploration in Python ## 

```python
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

# Time Range #
min_d = df.date.min()
max_d = df.date.max()
print('Min date: ', min_d)
print('Max date: ', max_d)
 ```

* There are 17379 observations and 17 columns. 
* All features are stored as float64 and only one column (dteday) has been stored as datetime. 
* No NULL values. 
* The dataset is presented as an aggregation of registered and casual consumers on a daily level and it goes as granular as hour.  
* Some features (season, weathersit) are stored as surrogate_keys and will need to be converted to corresponding label when plotting the data. 

The target variables are: 
* 'count'
* 'registered' 
* 'casual' 

Data time range

<img width="260" alt="Screenshot 2021-10-23 at 12 02 07" src="https://user-images.githubusercontent.com/73912794/138551824-39b8b26e-d94c-4a13-a039-e60b9b284c2b.png">

* Correlation coefficients show some positive correlation between ride's time ('hour') and temperature.
* It's interesting to observe that casual riders have stronger correlation with temperature compared to registered. 
* I'm assuming that casual riders are more related to leisure activities whereas registered are daily commuters

![heatmao](https://user-images.githubusercontent.com/73912794/138650525-be3b42e3-b195-43c6-a677-1db6a3e5037c.png)

I will focus on aggregating rides by month, season, weekday and hour to observe registered and casual riders behaviours and finally suggest action items to improve revenue. 

```python 
# Totals across time
df['year'] = df['date'].dt.year
totals = df.groupby('year', as_index=False)['totals'].sum()
_ = totals.plot.bar(x='year')
plt.title('Total Rides by Year')
```

![yearly_totals](https://user-images.githubusercontent.com/73912794/138652862-e0cf619c-9d54-4419-8f03-122133b41ff1.png)

```python
# Total registered and casual rides by year
reg_cas = df.groupby('year', as_index=False)[['registered', 'casual', 'totals']].sum()
_ = reg_cas[['year', 'registered', 'casual']].plot.bar(x='year')
plt.title('Bike usage for Registered and Casual by Year')
plt.ylabel('Count Rides')

reg_cas['registered'] = round((reg_cas['registered'] / reg_cas['totals']) * 100, 0)
reg_cas['casual'] = round((reg_cas['casual'] / reg_cas['totals']) * 100, 0)
print('Yearly Share of Registered and Casual\n', reg_cas)
```

<img width="331" alt="Screenshot 2021-10-25 at 09 33 06" src="https://user-images.githubusercontent.com/73912794/138653415-5df7608e-39c1-4fab-91b5-704842225380.png">

* There was an overall increase in 2012
* This interested both registered and casual riders 
* In 2012 the share of registered increased by 2 points and decreased by the same amount for casuals
* Assumption: probably marketing campaign have been launched to promote registrations and it would be interesting to calculate the conversion rate from casual to registered but the data doesn't provide that level of detail. 

I will have a look now at seasonality and monthly trends. 

```python 

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

```
* The monthly trend shows higher usage during milder seasons, winter traffic is low.
* On a sesonal level the share of casual riders seems to be particularly impacted by winter. 
* The distribution of rides across seasons shows and increasing trend as summer approaches (avg. increases and central tendency moves towards higher values). 

![monthly_trend](https://user-images.githubusercontent.com/73912794/138654129-6b3e16f5-bd7c-416d-8e31-c08c37bd310e.png)

![seasonal_trend_by_reg_cas](https://user-images.githubusercontent.com/73912794/138654921-62de0bef-dbe5-49e0-818a-21350162f242.png)

![seasonal_bp](https://user-images.githubusercontent.com/73912794/138655088-088933a1-728f-4fb5-ae37-3c629e86679e.png)


At this stage we observe an overall trend across seasons. I want to go on a smaller granular level (hours, weekdays) to observe differences between registered and casual. 

```python 
# Let's have a look at the weekdays and group by reg and cas
df['day_name'] = df.date.dt.day_name()
df['weekday'] = df.weekday.astype(int)
df['day_name'] = df.weekday.astype(str) + df.day_name
week_day = df.groupby('day_name', as_index=False)[['registered', 'casual']].sum().plot.bar(x='day_name')
plt.title('Registered and Casual Rides by Weekdays')
plt.show()
```

![weekly_reg_cas](https://user-images.githubusercontent.com/73912794/138657338-91c741c0-794c-4578-b75c-8060dbc9de55.png)

* Opposite trend for registered and casual
* Registered traffic remains high across the working days
* Casual are momentum is the weekend

```python
# Daily distribution by Registered and Casual
dist_day = df[['day_name', 'registered', 'casual']]
fig, ax = plt.subplots(2, 1)
sns.boxplot(dist_day['day_name'], dist_day['registered'], ax=ax[0])
ax[0].set_title('Weekday Distribution - Registered')
ax[0].set_xlabel("")
sns.boxplot(dist_day['day_name'], dist_day['casual'], ax=ax[1])
ax[1].set_title('Weekday Distribution - Casual')
ax[1].set_xlabel("")
```

![daily_boxplots_reg_cas](https://user-images.githubusercontent.com/73912794/138657631-348d2385-adee-4868-abd2-a3279252197f.png)

* The daily distribution for registered on weekdays is pretty stable showing that these rides might be really bounded to working hours
* Casuals distributions have higher averages in the weekends and 
* The outliers might be due to the spikes occurring in the commuting time.  

```python
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
```

* The registered weekly usage is strongly dictated by the working hours 
* Casual rides increase as registered decrease
* Casual rides are less impacted by working hours and tend to be stable across 10 am and late evening

![hourly_trend](https://user-images.githubusercontent.com/73912794/138658638-1a788223-cb9e-48cd-86c9-5f322db02bd9.png)


* The weekend trend takes for registered the same shape of casuals
* This shows that registered are particularly related to commuting and working hours but leisure is still one of the reason for biking.
* Casuals seem to be occasional drivers using the service more for leisure.

![hourly_trend_by_weekdays](https://user-images.githubusercontent.com/73912794/138658685-e0873935-b02c-4e9b-b558-adc97bac084b.png)


To make the analysis more readable for stakeholders, I will create two dimensional tables to be joined on season and weather. The final output file will be used in Tableau for visaulisations. 

```python 
# Create Dim Tables to merge #
dim_season = pd.DataFrame({'season_sk': [1, 2, 3, 4],
                           'season': ['winter', 'spring', 'summer', 'fall']})

dim_weather = pd.DataFrame({'weather_sk': [1, 2, 3, 4],
                            'weather': ['Few clouds, Partly cloudy, Partly cloudy',
                                        'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
                                        'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds',
                                        'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog']})

# Join the 3 tables on sk
data = df.merge(dim_season, how='inner', on='season_sk').merge(dim_weather, how='inner', on='weather_sk')

bike_share = data[
    ['instant', 'date', 'year', 'year_season', 'month_int', 'hour', 'holiday', 'weekday', 'workingday', 'season',
     'weather', 'temp', 'atemp', 'humidity', 'windspeed', 'casual', 'registered', 'totals']]

# Export cleaned data set as csv file and plot it into Tableau
# Converting into CSV and Save locally - This is only to be read into SQL
wf = bike_share.to_csv(path + 'bike_sharing_wf.csv',
                       header=True,
                       index=False)
```
