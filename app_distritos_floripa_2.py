
import streamlit as st
from streamlit_folium import folium_static
import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
from folium import plugins
from folium.plugins import MeasureControl
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap



url_bairros = 'https://raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/distritos_administrativosWGS84.geojson'
#style = {'fillcolor' : '#F5DEB3' , 'color' : '#8B0000'}

polygons = gpd.read_file(url_bairros)

#m = folium.Map (location = [-27.594605,-48.508875],
 #              tiles = 'openstreetmap',
 #              zoom_start =  12)

#folium.GeoJson(
 #  bairros,
  # name='bairros',
  # tooltip=folium.GeoJsonTooltip(fields=['nome', 'codigo_ibg']),
  # style_function=lambda x: style).add_to(m)

url_pontos_onibus = 'https://raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/pontos_onibus_2024_WGS84_TODOS.geojson'
points = gpd.read_file(url_pontos_onibus)

# Configuração da página
PAGE_CONFIG = {"page_title":"Aplicação de Mapas com Pandas", "page_icon":":smiley:", "layout":"centered"}
st.set_page_config(**PAGE_CONFIG)



def main():
    # Cria uma dropdown para escolher a regional
    polygons['nome'] = polygons['nome'].apply(lambda x: x.encode('latin1').decode('utf-8') if isinstance(x, str) else x)
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
    
 #Para meu controle, não sei pq o min e o max estão vindo com o mesmo valor, ai coloquei o -1 no min pra não dar erro
    print(pts_in_polys)
    print(points.crs)
    print(polygons.crs)
    print("minimo: ", bairros_filtrados['num_pto'].min())
    print("máximo: ", bairros_filtrados['num_pto'].max())
    print("pts_in_polys: ",bairros_filtrados['num_pto']) 
 
    #Slidebar para filtrar pelo número de pontos
    num_pontos = st.sidebar.slider(
    "Número de pontos de ônibus",
    int(bairros_filtrados['num_pto'].min()-int(bairros_filtrados['num_pto'].max()),
    int(bairros_filtrados['num_pto'].max()),
    (int(bairros_filtrados['num_pto'].min()-int(bairros_filtrados['num_pto'].max()), int(bairros_filtrados['num_pto'].max()))
)

    
    # Filtra os bairros pelo número de estacionamentos
    bairros_finais = bairros_filtrados[bairros_filtrados['num_pto'].between(num_pontos[0], num_pontos[1])]

    # Plota o histograma
    f = px.histogram(bairros_finais, x="num_pto", title="Distribuição dos Pontos de Ônibus")
    f.update_xaxes(title="Pontos de ônibus")
    f.update_yaxes(title="Número")
    st.plotly_chart(f)

    # Mapa com Folium
    m = folium.Map(location=[-27.594605,-48.508875], zoom_start=9)
    folium.Choropleth(
        geo_data=bairros_finais.to_json(),
        name='Pontos de ônibus por bairro',
        data=bairros_finais,
        columns=['nome', 'num_pto'],
        key_on='feature.properties.nome',
        fill_color='YlGn',
        legend_name='Pontos de ônibus por bairro ou distrito'
    ).add_to(m)
 
    locations = []
    for idx, row in points.iterrows():
     locations.append([row['geometry'].y, row['geometry'].x])

    m.add_children(MarkerCluster(locations=locations, name = 'Pontos de Ônibus de Florianópolis'))

    #for idx, row in points.iterrows():
     #locations.append([row['geometry'].y, row['geometry'].x])

    #HeatMap(locations,name = 'Mapa de Calor').add_to(m)
    
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
