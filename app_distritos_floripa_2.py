
import folium
from folium import plugins
from folium.plugins import MeasureControl
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import plotly.express as px



bairros = 'https:///raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/distritos_administrativosWGS84.geojson'
#style = {'fillcolor' : '#F5DEB3' , 'color' : '#8B0000'}

polygons = gpd.read_file(bairros)

#m = folium.Map (location = [-27.594605,-48.508875],
 #              tiles = 'openstreetmap',
 #              zoom_start =  12)

#folium.GeoJson(
 #  bairros,
  # name='bairros',
  # tooltip=folium.GeoJsonTooltip(fields=['nome', 'codigo_ibg']),
  # style_function=lambda x: style).add_to(m)

pontos_onibus = 'https:///raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/pontos_onibus_2024_WGS84_TODOS.geojson'
points = gpd.read_file(pontos_onibus)

# Configuração da página
PAGE_CONFIG = {"page_title":"Aplicação de Mapas com Pandas", "page_icon":":smiley:", "layout":"centered"}
st.set_page_config(**PAGE_CONFIG)



def main():
    # Cria uma dropdown para escolher a regional
    regionais = polygons['nome'].unique()
    regional_selecionada = st.sidebar.selectbox('Escolha a regional', regionais)

    # Filtra os bairros por regional selecionada
    bairros_filtrados = polygons[polygons['nome'] == regional_selecionada]

    # Conta pontos dentro de cada polígono filtrado
    pts_in_polys = []
    for i, poly in bairros_filtrados.iterrows():
        pts_in_this_poly = points[points.within(poly.geometry)]
        pts_in_polys.append(len(pts_in_this_poly))

    bairros_filtrados['num_pto'] = pts_in_polys

    # Slidebar para filtrar pelo número de estacionamentos
    num_estacionamentos = st.sidebar.slider("Número de estacionamentos", int(bairros_filtrados['num_pto'].min()), int(bairros_filtrados['num_pto'].max()), (int(bairros_filtrados['num_pto'].min()), int(bairros_filtrados['num_pto'].max())))
    
    # Filtra os bairros pelo número de estacionamentos
    bairros_finais = bairros_filtrados[bairros_filtrados['num_pto'].between(num_estacionamentos[0], num_estacionamentos[1])]

    # Plota o histograma
    f = px.histogram(bairros_finais, x="num_pto", title="Distribuição de Estacionamentos")
    f.update_xaxes(title="Estacionamentos")
    f.update_yaxes(title="Número")
    st.plotly_chart(f)

    # Mapa com Folium
    m = folium.Map(location=[-25.5, -49.3], zoom_start=9)
    folium.Choropleth(
        geo_data=bairros_finais.to_json(),
        name='Pontos de ônibus por bairro',
        data=bairros_finais,
        columns=['OBJECTID', 'num_pto'],
        key_on='feature.properties.OBJECTID',
        fill_color='YlGn',
        legend_name='Ponos de ônibus por bairro ou distrito'
    ).add_to(m)
    folium.LayerControl().add_to(m)
    folium_static(m)

if __name__ == '__main__':
    main()
    

"""
locations = []

for idx, row in points.iterrows():
    locations.append([row['geometry'].y, row['geometry'].x])

m.add_children(MarkerCluster(locations=locations, name = 'Pontos de Ônibus de Florianópolis'))

for idx, row in df.iterrows():
    locations.append([row['geometry'].y, row['geometry'].x])

HeatMap(locations,name = 'Mapa de Calor').add_to(m)


folium.LayerControl().add_to(m)
m.add_child(MeasureControl())

m"""
