#bibliotecas
from haversine import haversine 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
import inflection
from streamlit_folium import folium_static


df = pd.read_csv('zomato.csv')

st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout='wide'
)

# Aplica o estilo CSS com a largura máxima
# Define uma largura máxima responsiva com base na largura da tela
# Detecta a largura da tela

st.components.v1.html(
    f"""
    <script>
        var larguraTela = window.innerWidth;
        var larguraMaxima = Math.min(larguraTela, 1500);  // Ajuste o valor conforme necessário
        var style = document.createElement("style");
        style.textContent = 'div.reportview-container {{ max-width: ' + larguraMaxima + 'px; }}';
        document.head.appendChild(style);
    </script>
    """
)


#TRANSFORMAÇÕES

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

df = rename_columns(df)

df = df.loc[df['cuisines'] != 'nan']

df["cuisines"] = df["cuisines"].astype(str)

df = df.drop(columns = ['switch_to_order_menu'], axis = 1)

df['cuisines'] = df.loc[:, 'cuisines'].apply(lambda x: x.split(',')[0])

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

for i in range(df.shape[0]):
    df.loc[i, 'rating_color'] = color_name(df.loc[i,'rating_color'])

countries = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}

def country_name(country_id):
    return countries[country_id]
    
for i in range(df.shape[0]):
    df.loc[i, 'country_code'] = country_name(df.loc[i,'country_code'])


#===================================== PÁGINA ==========================================================

image_path = 'logo.png'
image = Image.open( image_path )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Fome Zero')

st.sidebar.markdown("""---""")

#==================================================================================
#Filtro de Países
#==================================================================================

country_options = st.sidebar.multiselect(
    'Escolha os Países que Deseja visualizar os Restaurantes',
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'India',
       'Indonesia', 'New Zeland', 'England'])

linhas_selecionadas = df['country_code'].isin(country_options)
df1 = df.loc[linhas_selecionadas, :]


#==================================================================================
#                                  SLIDER
#==================================================================================

st.markdown("# Fome Zero!")
st.markdown("## O Melhor lugar para encontrar seu mais novo restaurante favorito!")
st.markdown("### Temos as seguintes marcas dentro da nossa plataforma:")


#==================================================================================
#                                  Página
#===================================================================================

with st.container():
    col1,col2,col3,col4,col5 = st.columns(5 , gap='large')
    
    with col1:
        #quantidade de restaurantes cadastrados
        qntd_restaurantes = df.loc[:,'restaurant_name'].unique()
        col1.metric('Restaurantes Cadastrados',len(qntd_restaurantes))
    
    with col2:
        #Países cadastrados
        paises_unicos = df.loc[:,'country_code'].unique()
        col2.metric('Países Cadastrados',len(paises_unicos))
    
    with col3:
        cidades_unicos = df.loc[:,'city'].unique()
        col3.metric('Cidades Cadastradas', len(cidades_unicos))
                
    
    with col4:
        avaliacoes = df.loc[:,'votes'].sum()
        col4.metric('Avaliações Feitas na Plataforma', avaliacoes)

    with col5:
        culinaria = df.loc[:,'cuisines'].unique()
        col5.metric('Tipos de Culinárias Oferecidas', len(culinaria))
                
with st.container():
    st.markdown('### Mapa')
        
    columns = [
    'country_code','restaurant_id','latitude', 'longitude'
    ]
    columns_grouped = ['country_code','restaurant_id']
    data_plot = df.loc[:, columns].groupby( columns_grouped ).median().reset_index()
    data_plot = data_plot[data_plot['country_code'] != 'NaN']
    data_plot = data_plot[data_plot['restaurant_id'] != 'NaN']
    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
      folium.Marker( [location_info['latitude'],
                      location_info['longitude']],
                    popup=location_info[['country_code', 'restaurant_id']] ).add_to( map )
    folium_static( map, width=1024 , height=600 )



st.markdown(
    """
     Ask for Help
""")
st.write(' Powered by [Strieder](https://www.linkedin.com/in/henrique-strieder/)')

