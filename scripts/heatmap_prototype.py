import os
import datetime
import pytz

import matplotlib.pyplot as plt
import pandas as pd
import osmnx as ox

from peewee import *

#ENVIRONMENT VARIABLES
DATABASE = os.environ['DATABASE']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
HOST = os.environ['HOST']
PORT = int(os.environ['PORT'])

mysql_db = MySQLDatabase(DATABASE, user=USERNAME, password=PASSWORD, host=HOST, port=PORT)
mysql_db.connect()
query = mysql_db.execute_sql('SELECT * FROM posicoes LIMIT 5000')
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

#CONSULTA BBOX DO BAIRRO
# 'bbox_east': -43.3241244, 'bbox_north': -22.8591909, 'bbox_south': -22.8830815, 'bbox_west': -43.349747}
bairro_gdf = ox.gdf_from_place('Madureira, Rio de Janeiro, Rio de Janeiro, Brazil')
bairro_latlong = {'lat': bairro_gdf[['bbox_north', 'bbox_south']].values[0],
                  'long': bairro_gdf[['bbox_east', 'bbox_west']].values[0]}

# RESTRINGE OS PONTOS AO LATLONG DO BAIRRO
for item in ['lat', 'long']:
    gps_data = gps_data[gps_data[item].apply(lambda x: min(bairro_latlong[item]) <= x <= max(bairro_latlong[item]))]

bairro_graph = ox.graph_from_place('Madureira, Rio de Janeiro, Rio de Janeiro, Brazil', network_type='drive')
bairro_projected = ox.project_graph(bairro_graph)

fig, ax = ox.plot_graph(bairro_graph, show=False, close=False, fig_height=15, fig_width=15)
for ordem, lat, long in zip(gps_data['ordem'].values, gps_data['lat'].values, gps_data['long'].values):
    ax.scatter(long, lat, c='red', s=100, alpha=0.3)
    ax.annotate(ordem, (long, lat))
plt.savefig('madureira.png')
