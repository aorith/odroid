#!/usr/bin/env python3
import datetime

import sqlite3
import pandas as pd
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
# note: set Agg in /etc/matplotlibrc
plt.rcParams['figure.figsize'] = [16, 8]

# warnings of pandas
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# Needed date values for sql querys
NOW = datetime.datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
YESTERDAY = (NOW - datetime.timedelta(1)).strftime("%Y-%m-%d")

##### CONSTANTS
IMG_PATH = '/var/www/html/tempsensor/imgs/'
DB_PATH = '/home/aorith/githome/odroid/tempsensor/data/temperature.db'
##############

### START DB WORK ##########################################################################################
# connect to the database
conn = sqlite3.connect(DB_PATH)

### TODAYS DATA #####################################################
query = f"SELECT * FROM temperature WHERE date LIKE '{TODAY} %';"

dft = pd.read_sql_query(query, conn)

# convert to datetime excluding year-month-day
dft["date"] = pd.to_datetime(dft["date"])
dft["date"] = pd.DatetimeIndex(dft["date"]).time
dft["date"] = dft["date"].apply(lambda t: t.replace(second=0))
dft.set_index("date", inplace=True)
#####################################################################

### YESTERDAYS DATA #################################################
query = f"SELECT * FROM temperature WHERE date LIKE '{YESTERDAY} %';"

dfy = pd.read_sql_query(query, conn)

# convert to datetime excluding year-month-day
dfy["date"] = pd.to_datetime(dfy["date"])
dfy["date"] = pd.DatetimeIndex(dfy["date"]).time
dfy["date"] = dfy["date"].apply(lambda t: t.replace(second=0))
dfy.set_index("date", inplace=True)
#####################################################################

### ALL TIME DATA ###################################################
query = f"SELECT * FROM temperature;"

dfa = pd.read_sql_query(query, conn)

dfa["date"] = pd.to_datetime(dfa["date"])
dfa["date"] = dfa["date"].apply(lambda t: t.replace(second=0))
dfa.set_index("date", inplace=True)

#####################################################################

# Close connection
conn.close()
#### END DB WORK ############################################################################################


### HELPER FUNCTIONS #################################################

def rolling_mean(df, col, val=12):
    return df[col].rolling(window=val, min_periods=1).mean().dropna()

######################################################################


#### TODAY VS YESTERDAY #########################

fig, ax = plt.subplots()
ax.set_facecolor('#fcffe8')
ax.plot(rolling_mean(dft, 'ctemp'), color='r', label='℃ today', linewidth=4)
ax.plot(rolling_mean(dfy, 'ctemp'), color='darkred', label='℃ yesterday', alpha=0.3, linewidth=2, linestyle='--')

# y axis config for temp
ax.set_ylabel('Celsius', color='r')
ax.tick_params('y', colors='r')

# rotate and align tick labels
#fig.autofmt_xdate()

# title and x label
ax.set_title('Today vs Yesterday')
ax.set_xlabel('Time')

# humidity
ax1 = ax.twinx()
ax1.plot(rolling_mean(dft, 'hum'), color='b', label='Humidity %', linewidth=3)
ax1.plot(rolling_mean(dfy, 'hum'), color='darkblue', label='Humidity % yesterday', alpha=0.3, linewidth=2, linestyle='--')
# y axis config for humidity
ax1.set_ylabel('Humidity %', color='b')
ax1.tick_params('y', colors='b')


fig.tight_layout()
ax.grid()
ax.legend(loc='upper left')
ax1.legend(loc='upper right')
#fig.legend(loc="upper right", bbox_to_anchor=(0.92, 0.92))
fig.savefig(IMG_PATH + 'today_vs_yesterday.png', dpi=65, facecolor='w', edgecolor='k', figsize=(16, 8))


#### ALL TIME DATA ############################
# TODO: check this when there is more data:
rolling_wind_val = int(len(dfa) / 24)

fig, ax = plt.subplots()
ax.set_facecolor('#fcffe8')
ax.plot(rolling_mean(dfa, 'ctemp', rolling_wind_val), color='r', label='℃ ', linewidth=4)

# y axis config for temp
ax.set_ylabel('Celsius', color='r')
ax.tick_params('y', colors='r')

# rotate and align tick labels
fig.autofmt_xdate()

# title and x label
ax.set_title('All Time Data')
ax.set_xlabel('Date')

# humidity
ax1 = ax.twinx()
ax1.plot(rolling_mean(dfa, 'hum', rolling_wind_val), color='b', label='Humidity %', linewidth=3)
# y axis config for humidity
ax1.set_ylabel('Humidity %', color='b')
ax1.tick_params('y', colors='b')

fig.tight_layout()
ax.grid()
ax.legend(loc='upper left')
ax1.legend(loc='upper right')
#fig.legend(loc="upper right", bbox_to_anchor=(0.92, 0.92))
fig.savefig(IMG_PATH + 'all_time_data.png', dpi=65, facecolor='w', edgecolor='k', figsize=(16, 8))



#### MAX/MEANS ###################################################
fig, ax = plt.subplots()

ax.bar('Today', max(dft['ctemp']))
ax.bar('Yesterday', max(dfy['ctemp']))
ax.bar('All times', max(dfa['ctemp']))
ax.set_title("Maximum Temperature")
ax.set_ylabel("Celsius")

fig.savefig(IMG_PATH + 'maximum_temp.png', dpi=60, facecolor='w', edgecolor='k', figsize=(8, 6))

fig, ax = plt.subplots()

ax.bar('Today', max(dft['hum']))
ax.bar('Yesterday', max(dfy['hum']))
ax.bar('All times', max(dfa['hum']))
ax.set_title("Maximum Humidity")
ax.set_ylabel("Humidity")

fig.savefig(IMG_PATH + 'maximum_hum.png', dpi=60, facecolor='w', edgecolor='k', figsize=(8, 6))

# means

fig, ax = plt.subplots()

ax.bar('Today', dft['ctemp'].mean())
ax.bar('Yesterday', dfy['ctemp'].mean())
ax.bar('All times', dfa['ctemp'].mean())
ax.set_title("Mean Temperature")
ax.set_ylabel("Celsius")

fig.savefig(IMG_PATH + 'mean_temp.png', dpi=60, facecolor='w', edgecolor='k', figsize=(8, 6))

fig, ax = plt.subplots()

ax.bar('Today', dft['hum'].mean())
ax.bar('Yesterday', dfy['hum'].mean())
ax.bar('All times', dfa['hum'].mean())
ax.set_title("Mean Humidity")
ax.set_ylabel("Humidity")

fig.savefig(IMG_PATH + 'mean_hum.png', dpi=60, facecolor='w', edgecolor='k', figsize=(8, 6))
##################################################################


