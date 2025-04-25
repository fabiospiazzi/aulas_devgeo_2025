
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


url_bairros = 'https://raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/distritos_administrativosWGS84_c1.geojson'
polygons = gpd.read_file(url_bairros)

url_pontos_onibus = 'https://raw.githubusercontent.com/fabiospiazzi/aulas_devgeo_2025/main/pontos_onibus_2024_WGS84_TODOS.geojson'
points = gpd.read_file(url_pontos_onibus)

#Configuração da página
PAGE_CONFIG = {"page_title":"Aplicação de Mapas com Pandas", "page_icon":":smiley:", "layout":"centered"}
st.set_page_config(**PAGE_CONFIG)

def main():

    st.title("Mapa Interativo de Pontos de Ônibus em Florianópolis 🚌")
    # Cria um dropdown para escolher a regional
    #polygons['nome'] = polygons['nome'].apply(lambda x: x.encode('latin1').decode('utf-8') if isinstance(x, str) else x)
    regionais = polygons['nome'].unique()
    regional_selecionada = st.sidebar.selectbox('Escolha a regional', regionais)

    # Filtra os bairros por região ou distrito selecionada
    bairros_filtrados = polygons[polygons['nome'] == regional_selecionada]

    # Conta pontos dentro de cada polígono filtrado
    pts_in_polys = []
    for i, poly in bairros_filtrados.iterrows():
        pts_in_this_poly = points[points.within(poly.geometry)]
        pts_in_polys.append(len(pts_in_this_poly))

       
    bairros_filtrados['num_pto'] = pts_in_polys
    
 #Para meu controle, não sei pq o min e o max estão vindo com o mesmo valor. O sliderbar não funcinou.
    print(pts_in_polys)
    print(points.crs)
    print(polygons.crs)
    print("minimo: ", bairros_filtrados['num_pto'].min())
    print("máximo: ", bairros_filtrados['num_pto'].max())
    print("pts_in_polys: ",bairros_filtrados['num_pto']) 
 
 #Slidebar para filtrar pelo número de pontos
 #    num_pontos = st.sidebar.slider(
 #   "Número de pontos de ônibus",
 #   int(bairros_filtrados['num_pto'].min()),
 #   int(bairros_filtrados['num_pto'].max()),
 #   (int(bairros_filtrados['num_pto'].min())-(int(bairros_filtrados['num_pto'].max()), int(bairros_filtrados['num_pto'].max())))
 #)

    
    # Filtra os bairros pelo número de estacionamentos
 #   bairros_finais = bairros_filtrados[bairros_filtrados['num_pto'].between(num_pontos[0], num_pontos[1])]

 # Plota o histograma
 #   f = px.histogram(bairros_finais, x="num_pto", title="Distribuição dos Pontos de Ônibus")
 #   f.update_xaxes(title="Pontos de ônibus")
 #   f.update_yaxes(title="Número")
 #   st.plotly_chart(f)

 # Mapa com Folium
 #  m = folium.Map(location=[-27.594605,-48.508875], zoom_start=13)
 
 
 
 # Calcula o centroide do bairro selecionado para dar zoom direto no bairro
    centroide = bairros_filtrados.geometry.centroid.iloc[0]
    m = folium.Map(location=[centroide.y, centroide.x], zoom_start=12)
    folium.Choropleth(
        geo_data=bairros_filtrados.to_json(),
        name='Pontos de ônibus por bairro',
        data=bairros_filtrados,
        columns=['nome', 'num_pto'],
        key_on='feature.properties.nome',
        fill_color='YlGn',
        legend_name='Pontos de ônibus por bairro ou distrito'
    ).add_to(m)

  #Mostra os pontos de ônbius em todo o município
    #locations = []
    #for idx, row in points.iterrows():
     #locations.append([row['geometry'].y, row['geometry'].x])
    
     #Adiciona marcador no centro do bairro
    folium.Marker(
         location=[centroide.y, centroide.x],
         popup=f"Bairro: {regional_selecionada}",
         icon=folium.Icon(color='blue', icon='info-sign')
     ).add_to(m) 

    #Mostra os pontos de ônibus somente no bairro selecionado
    locations = []
    for i, poly in bairros_filtrados.iterrows():
        pts_in_this_poly = points[points.within(poly.geometry)]
        for _, row in pts_in_this_poly.iterrows():
          locations.append([row.geometry.y, row.geometry.x])

    #Adiciona os pontos selecionados no mapa em formato e cluster
    
    folium.plugins.MarkerCluster(locations=locations, name='Pontos de Ônibus').add_to(m)
 
    HeatMap(locations,name = 'Mapa de Calor').add_to(m)
    
    folium.LayerControl().add_to(m)
    folium_static(m)


if __name__ == '__main__':
    main()
    
