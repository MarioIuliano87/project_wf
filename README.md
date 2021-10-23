# Wunderflat Case Study # 

## Objective ##

The goal of this analysis is to identify a key finding(s) from the data that would help drive
more revenue to the business. 

## Approach ## 

1. Business Understanding
2. Upload data into DBeaver ??? 
3. High level exploration in Python 
4. Custom SQL will be used as data source for Tableau ???
5. Insights

 
 ## Business Understanding ## 
 
 Now we have the data. 
 
 How can I support the businees towards generating more revenue? 
 
 Simple question: How do bike shares programs generate revenue? 
 
 - Memebership plan (annual fee) 
 - Pay-as-you-go plan
 
The pay-as-you-go plan might be consumed by customers who occasionally commute within the city or bus/train/car drivers who tend to prefer other transports. 

Although increasing casual commuters will still represent a source of revenue, the most significant growth comes from long-term consumers.

**I will use the data to explore opportunities to increase the share of registered customers over casuals**


 ## Data Upload ##

The original file is in xlsx format and will need **to be converted into flat file csv to be queried into DBeaver**. 

```python
import pandas as pd

path = '/Users/iuliano/Documents/Proj/'

# Reading the data
df = pd.read_excel(path + 'Dataset - Case Study - BI Analyst Wunderflats.xlsx')

# Converting into CSV and Save locally

wf = df.to_csv(path + 'bike_sharing_wf.csv',
               header=True,
               index=False)
 ```
 
 The output csv file has been uploaded in DBeaver to be queried and analysed. 
 
 
 ![Screenshot 2021-10-23 at 11 38 39](https://user-images.githubusercontent.com/73912794/138551159-6fb1d7e6-d426-475e-abf3-6826eeebea71.png)


## High level exploration in Python ## 

The following questions will be answered in this part: 

- Dataset shape (rows, columns) 
- Data types 
- Null values? 

```python 

print('Rows: ', df.shape[0])
print('Columns: ', df.shape[1])

print(df.info())

print('Total NULL Values per Columns\n', df.isna().sum())
```

There are 17379 observations and 17 columns. 
All features are stored as float64 and only one column (dteday) has been stored as datetime. 
No NULL values. 

The target variables are: 
- 'count'
- 'registered' 
- 'casual' 

The dataset is presented as an aggregation of registered and casual consumers on a daily level and it goes as granular as hour.  

Some features (season, weathersit) are stored as surrogate_keys and will need to be converted to corresponding label when plotting the data. 

'Instant' column is an index. 

### Cleaning featur names and assign labels to SKs ###

I want to rename some columns to make the dataset more readable (the modified datasource might even become a shared source across the product team for quick reporting). 

```python 
# Rename sk columns #
data = df.rename(columns={'dteday': 'date',
                          'yr': 'year_sk',
                          'mnth': 'month_int',
                          'hr': 'hour',
                          'weathersit': 'weather_sk',
                          'hum': 'humidity',
                          'season': 'season_sk',
                          'cnt': 'totals'})

# Create Dim Tables and Merge #
dim_season = pd.DataFrame({'season_sk': [1, 2, 3, 4],
                           'season': ['winter', 'spring', 'summer', 'fall']})

dim_weather = pd.DataFrame({'weather_sk': [1, 2, 3, 4],
                            'weather': ['Few clouds, Partly cloudy, Partly cloudy',
                                        'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
                                        'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds',
                                        'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog']})

# Join the 3 tables on sk
data = data.merge(dim_season, how='inner', on='season_sk').merge(dim_weather, how='inner', on='weather_sk')

# Converting Year
data['year'] = data.year_sk.map({1: '2011',
                                 0: '2012'})

# Dataset for analysis
bike_share = data[['instant', 'date', 'season', 'hour',
                   'year', 'month_int', 'holiday', 'weekday',
                   'workingday', 'weather', 'temp', 'atemp',
                   'humidity', 'windspeed', 'casual', 'registered', 'totals']]
     
```

**Which Time Range do we have?** 

```python 
# Time Range #
min_d = df.dteday.min()
max_d = df.dteday.max()
print('Min date: ',  min_d)
print('Max date: ',  max_d)
``` 

<img width="260" alt="Screenshot 2021-10-23 at 12 02 07" src="https://user-images.githubusercontent.com/73912794/138551824-39b8b26e-d94c-4a13-a039-e60b9b284c2b.png">






