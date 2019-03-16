import os
import datetime
import pytz

import matplotlib.pyplot as plt
import pandas as pd
import osmnx as ox
import numpy as np

from peewee import *

#ENVIRONMENT VARIABLES
DATABASE = os.environ['DATABASE']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
HOST = os.environ['HOST']
PORT = int(os.environ['PORT'])

mysql_db = MySQLDatabase(DATABASE, user=USERNAME, password=PASSWORD, host=HOST, port=PORT)
mysql_db.connect()
query = mysql_db.execute_sql('SELECT * FROM posicoes posicoes WHERE `LINHA` = "409"')
mysql_db.close()

data_list = list()

for item in query:
    registro = {'timestamp': item[0],
                'ordem': item[1],
                'linha': item[2],
                'lat': item[3],
                'long': item[4],
                'velocidade': item[5]}
    data_list.append(registro)

df = pd.DataFrame(data_list)
columns = ['timestamp', 'ordem', 'linha', 'lat', 'long', 'velocidade']
df = df[columns]

gps_data = df.copy()
tz = pytz.timezone('America/Sao_Paulo')
gps_data['datetime'] = gps_data['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=tz))

#CONSULTA BBOX DO LOCAL
location_gdf = ox.gdf_from_place('Rio de Janeiro, Rio de Janeiro, Rio de Janeiro, Brazil')
location_latlong = {'lat': location_gdf[['bbox_north', 'bbox_south']].values[0],
                  'long': location_gdf[['bbox_east', 'bbox_west']].values[0]}

# RESTRINGE OS PONTOS AO LOCAL
for item in ['lat', 'long']:
    gps_data = gps_data[gps_data[item].apply(lambda x: min(location_latlong[item]) <= x <= max(location_latlong[item]))]

# IDENTIFICA E REMOVE OUTLIERS
data_mean, data_std = np.mean(gps_data['lat']), np.std(gps_data['lat'])
cut_off = data_std * 3
lower, upper = data_mean - cut_off, data_mean + cut_off
gps_data = gps_data[gps_data['lat'].apply(lambda x : lower < x < upper)]

bairro_graph = ox.graph_from_place('Rio de Janeiro, Rio de Janeiro, Rio de Janeiro, Brazil', network_type='drive')

fig, ax = ox.plot_graph(bairro_graph, show=False, close=False, fig_height=45, fig_width=135)
for lat, long in zip(gps_data['lat'].values, gps_data['long'].values):
    ax.scatter(long, lat, c='red', s=100, alpha=0.3)
plt.savefig('409.png')
