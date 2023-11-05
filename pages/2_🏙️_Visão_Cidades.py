#===================================================================================
#bibliotecas
#===================================================================================

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

st.set_page_config(page_title='Visão Cidades', page_icon='🏙️', layout='wide')

#===================================================================================
#TRANSFORMAÇÕES
#===================================================================================

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

#===================================================================================

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
    
#===================================================================================

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

#==================================================================================
#LAYOUT STREAMLIT - Barra Lateral
#==================================================================================

st.title('🏙️ Visão Cidades')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

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
df = df.loc[linhas_selecionadas, :]

#===================================================================================
#                            Final - Barra Lateral
#===================================================================================

st.sidebar.markdown("""---""")
st.sidebar.write('### Powered by [Strieder](https://www.linkedin.com/in/henrique-strieder/)')

#===================================================================================
#                            Layout no Streamlit
#===================================================================================

#1. Qual o nome da cidade que possui mais restaurantes registrados?
#2. Qual o nome da cidade que possui mais restaurantes com nota média acima de 4?
#3. Qual o nome da cidade que possui mais restaurantes com nota média abaixo de 2.5?
#4. Qual o nome da cidade que possui o maior valor médio de um prato para dois?

#5. Qual o nome da cidade que possui a maior quantidade de tipos de culinária distintas?
#6. Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem reservas?
#7. Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem entregas? 
#8. Qual o nome da cidade que possui a maior quantidade de restaurantes que aceitam pedidos online?

tab1, tab2 = st.tabs(['Visão Geográfica', 'Visão Tática'])

#1. Qual o nome da cidade que possui mais restaurantes registrados?
#2. Qual o nome da cidade que possui mais restaurantes com nota média acima de 4?
#3. Qual o nome da cidade que possui mais restaurantes com nota média abaixo de 2.5?
#4. Qual o nome da cidade que possui o maior valor médio de um prato para dois?

#==========================================================================================================================================================
#                                                                  Tab 1 - visão Geográfica
#==========================================================================================================================================================

with tab1:
    
    with st.container():
                
        col1,col2 = st.columns(2 , gap='large')
        
        with col1:
            #Qual o nome da cidade que possui mais restaurantes registrados           
            st.markdown('Quantidade de Restaurantes por Cidade')
            dfaux = df.loc[:, ['city','restaurant_name']].groupby('city').count().reset_index().sort_values('restaurant_name', ascending=False)
            dfaux.columns = ['city', 'restaurant_name']
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='restaurant_name',labels={'city':'Cidades',
                                                                                'restaurant_name':'Quantidade de Restaurantes'}), use_container_width=True)
            

        with col2:
            #Qual o nome da cidade que possui mais restaurantes com nota média acima de 4?
            st.markdown('Quantidade de Restaurantes por Cidade que Possuem Nota Média Maior ou Igual a 4')
            linhas = df['aggregate_rating'] >= 4
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['city','restaurant_name']].groupby('city').count().reset_index().sort_values('restaurant_name', ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='restaurant_name',labels={'city':'Cidades',
                                                                                'restaurant_name':'Quantidade de Restaurantes'}), use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------
            
    with st.container():
        
        col1, col2 = st.columns(2)
        
        with col1:
            #Qual o nome da cidade que possui mais restaurantes com nota média abaixo de 2.5?
            st.markdown('Quantidade de Restaurantes por Cidade que Possuem Nota Média Menor ou Igual a 2.5')
            linhas = df['aggregate_rating'] <= 2.5
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['city','restaurant_name']].groupby('city').count().reset_index().sort_values('restaurant_name', ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='restaurant_name',labels={'city':'Cidades',
                                                                                'restaurant_name':'Quantidade de Restaurantes'}), use_container_width=True)
            
            
        with col2:
            #Qual o nome da cidade que possui o maior valor médio de um prato para dois?
            st.markdown('Custo Médio para Duas Pessoas')
            dfaux = df.loc[:, ['city','average_cost_for_two']].groupby('city').mean().reset_index().sort_values('average_cost_for_two', ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='average_cost_for_two',labels={'city':'Cidades',
                                                      'average_cost_for_two':'Custo Médio para Duas Pessoas'}), use_container_width=True)

#==========================================================================================================================================================
#                                                                  Tab 2 - visão Tática
#==========================================================================================================================================================

#5. Qual o nome da cidade que possui a maior quantidade de tipos de culinária distintas?
#6. Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem reservas?
#7. Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem entregas? 
#8. Qual o nome da cidade que possui a maior quantidade de restaurantes que aceitam pedidos online?

with tab2:
    with st.container():
                
        col1,col2 = st.columns(2 , gap='large')
        
        with col1:
            #Qual o nome da cidade que possui a maior quantidade de tipos de culinária distintas?     
            st.markdown('Cidades que Possuem Maior Diversidade de Culinárias')
            dfaux = df.loc[:, ['city','cuisines']].groupby('city').count().reset_index().sort_values('cuisines', ascending=False)
            dfaux.columns = ['city', 'cuisines']
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='cuisines',labels={'city':'Cidades',
                                                                                'cuisines':'Quantidade de Culinárias Distintas'}), use_container_width=True)
            

        with col2:
            #Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem reservas?
            st.markdown('Cidades que Possuem maior Quantidade de Restaurantes que Fazem Reservas')
            dfaux = df.loc[:, ['city','has_table_booking']].groupby('city').sum().reset_index().sort_values('has_table_booking', ascending=False)
            
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='has_table_booking',labels={'city':'Cidades',
                                                                                'has_table_booking':'Quantidade de Restaurantes'}), use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------
            
    with st.container():
        
        col1, col2 = st.columns(2)
        
        with col1:
            #Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem entregas? 
            st.markdown('Cidades que Possuem maior Quantidade de Restaurantes que Fazem Entregas')
            dfaux = df.loc[:, ['city','is_delivering_now']].groupby('city').sum().reset_index().sort_values('is_delivering_now', ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='is_delivering_now',labels={'city':'Cidades',
                                                                                'is_delivering_now':'Quantidade de Restaurantes'}), use_container_width=True)
            
            
        with col2:
            #Qual o nome da cidade que possui a maior quantidade de restaurantes que aceitam pedidos online?
            st.markdown('Custo Médio para Duas Pessoas')
            dfaux = df.loc[:, ['city','has_online_delivery']].groupby('city').sum().reset_index().sort_values('has_online_delivery', ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='city', y='has_online_delivery',labels={'city':'Cidades',
                                                      'has_online_delivery':'Custo Médio para Duas Pessoas'}), use_container_width=True)