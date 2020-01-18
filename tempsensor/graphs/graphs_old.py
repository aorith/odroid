#!/usr/bin/env python3
import sqlite3
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
# note: set Agg in /etc/matplotlibrc
plt.rcParams['figure.figsize'] = [15, 7]
import numpy as np
import datetime

now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
yesterday = (now - datetime.timedelta(1)).strftime("%Y-%m-%d")

##### CONSTANTS

IMG_PATH = '/var/www/html/tempsensor/imgs/'

##############


conn = sqlite3.connect('/home/aorith/tempsensor/data/temperature.db')
c = conn.cursor()

# QUERY
query = f"SELECT * FROM temperature WHERE date LIKE '{today} %';"

c.execute(query)
data_today = c.fetchall()
data_today = np.array(data_today)

# QUERY
query = f"SELECT * FROM temperature WHERE date LIKE '{yesterday} %';"

c.execute(query)
data_yesterday = c.fetchall()
data_yesterday = np.array(data_yesterday)


# Close connection
conn.close()
#### END DB WORK ####

#### HELPER FUNCTIONS

# hide every N tick:
def hide_ticks(ax):
    total = len(ax.xaxis.get_major_ticks())
    max_x = 18
    r_count = 0
    idx = np.round(np.linspace(0, total - 1, max_x)).astype(int)

    for tick in ax.xaxis.get_major_ticks():
        if r_count not in idx:
            tick.set_visible(False)
        r_count += 1


    total = len(ax.get_yticklabels())
    max_y = 15
    r_count = 0
    idx = np.round(np.linspace(0, total -1, max_y)).astype(int)

    for tick in ax.yaxis.get_major_ticks():
        if r_count not in idx:
            tick.set_visible(False)
        r_count += 1

#### MATPLOTLIB WORK ####

str_data_today = []
for d in data_today[:,0]:
    newdate = d.split(' ')[1]
    newdate = newdate.split(':')
    newdate = newdate[0] + ':' + newdate[1]
    str_data_today.append(newdate)

str_data_yesterday = []
for d in data_yesterday[:,0]:
    newdate = d.split(' ')[1]
    newdate = newdate.split(':')
    newdate = newdate[0] + ':' + newdate[1]
    str_data_yesterday.append(newdate)

# min and max temp
#max_temp = max(max(data_yesterday[:,1]), max(data_today[:,1]))
#min_temp = min(min(data_yesterday[:,1]), min(data_today[:,1]))


# TODAY VS YESTERDAY
fig, ax = plt.subplots()
ax.plot(str_data_today, data_today[:,1], color='r', label='Celsius')
ax.plot(str_data_yesterday, data_yesterday[:,1], color='darkred', label='Celsius Yesterday', alpha=0.3, linewidth=0.7)
# y axis config for temp
ax.set_ylabel('Celsius', color='r')
ax.tick_params('y', colors='r')

# rotate and align tick labels
fig.autofmt_xdate()

# title and x label
ax.set_title('Temperature')
ax.set_xlabel('Date')

# humidity
ax1 = ax.twinx()
ax1.plot(str_data_today, data_today[:,2], color='b', label='Humidity %')
ax1.plot(str_data_yesterday, data_yesterday[:,2], color='darkblue', label='Humidity % yesterday', alpha=0.3, linewidth=0.7)
# y axis config for humidity
ax1.set_ylabel('Humidity %', color='b')
ax1.tick_params('y', colors='b')

# hide labels every N
hide_ticks(ax)
hide_ticks(ax1)

fig.tight_layout()
fig.legend(loc="upper right", bbox_to_anchor=(0.92, 0.92))
fig.savefig(IMG_PATH + 'today.png', dpi=120, facecolor='w', edgecolor='k', figsize=(16, 8))
