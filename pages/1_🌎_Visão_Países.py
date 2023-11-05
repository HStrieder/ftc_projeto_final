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

st.set_page_config(page_title='Visão Países', page_icon='🌎', layout='wide')

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

#==================================================================================
#LAYOUT STREAMLIT - Barra Lateral
#==================================================================================

st.title('🌎 Visão Países')
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
#                                  SLIDER
#===================================================================================

st.sidebar.markdown("""---""")
st.sidebar.write('### Powered by [Strieder](https://www.linkedin.com/in/henrique-strieder/)')

#===================================================================================
#                                  LAYOUT
#===================================================================================

#PAÍS

#1. Qual o nome do país que possui mais cidades registradas? gráfico de barra
#2. Qual o nome do país que possui mais restaurantes registrados? gráfico de barra
#8. Qual o nome do país que possui, na média, a maior quantidade de avaliações registrada? gráfico de linhas
#11. Qual a média de preço de um prato para dois por país? gráfico de linhas

tab1, tab2, tab3 = st.tabs(['Visão Geográfica', 'Visão Tática', 'Visão Gerencial'])

with tab1:

    with st.container():
        #quantidade de restaurantes por país
        st.markdown('Quantidade de Restaurantes por País')
        dfaux = df.loc[:, ['country_code', 'restaurant_id']].groupby('country_code').count().reset_index()
        dfaux.columns = ['country_code', 'restaurant_id']
    
        
        # gráfico
        st.plotly_chart(px.bar( dfaux, x='country_code', y='restaurant_id',labels={'country_code':'Países', 'restaurant_id':'Quantidade de Restaurantes'} ),
                        use_container_width=True )
    
#-------------------------------------------------------------------------------------------------------------------------------------------------
    
    with st.container():
        #quantidade de cidades por país
        st.markdown('Quantidade de Cidades Registradas por País')
        dfaux = df.loc[:, ['country_code','city']].groupby('country_code').nunique().reset_index().sort_values('city', ascending=False)
        dfaux.columns = ['country_code', 'city']
        
        # gráfico
        st.plotly_chart(px.bar( dfaux, x='country_code', y='city',labels={'country_code':'Países', 'restaurant_id':'Quantidade de Restaurantes'} ),
                        use_container_width=True )
    
#-------------------------------------------------------------------------------------------------------------------------------------------------
# Container com colunas
#-------------------------------------------------------------------------------------------------------------------------------------------------
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            #média de avaliações por país           
            st.markdown('Média de Avaliações Feitas por País')
            dfaux = df.loc[:, ['country_code','votes']].groupby('country_code').mean().reset_index().sort_values('votes', ascending=False)
            dfaux.columns = ['country_code', 'votes']
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='votes',labels={'country_code':'Países',
                                                                                       'votes':'Quantidade de Avaliações'}), use_container_width=True)
    
        with col2:
            #média de preço de um prato por país
            st.markdown('Média de Preço de um Prato para duas pessoas por País')
            dfaux = df.loc[:, ['country_code','average_cost_for_two']].groupby('country_code').mean().reset_index().sort_values('average_cost_for_two',
                                                                                                                                ascending=False)
            dfaux.columns = ['country_code', 'average_cost_for_two']
            
             #gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='average_cost_for_two',labels={'country_code':'Países',
                                                                                             'average_cost_for_two':'Preço de um Prato para duas pessoas'})
                                                                                             ,use_container_width=True)


#==========================================================================================================================================================
#                                                                  Tab 2 - visão tática
#==========================================================================================================================================================

#3. Qual o nome do país que possui mais restaurantes com o nível de preço igual a 4 registrados? barras
#4. Qual o nome do país que possui a maior quantidade de tipos de culinária distintos? barra
#5. Qual o nome do país que possui a maior quantidade de avaliações feitas? barra
#6. Qual o nome do país que possui a maior quantidade de restaurantes que fazem entrega? grafico barras
#7. Qual o nome do país que possui a maior quantidade de restaurantes que aceitam reservas? gráfico de barras

with tab2:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            #países que possuem mais restaurantes com o nível de preço igual a 4 registrados
            linhas = df['price_range'] == 4
            df1 = df.loc[linhas,:].copy()           
            st.markdown('Países que possuem mais Restaurantes com nível igual a 4')
            dfaux = df1.loc[:, ['country_code','restaurant_name']].groupby('country_code').count().reset_index().sort_values('restaurant_name',
                                                                                                                             ascending=False)
            dfaux.columns = ['country_code', 'restaurant_name']
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='restaurant_name',labels={'country_code':'Países',
                                                             'restaurant_name':'Quantidade de Restaurantes'}), use_container_width=True)
    
        with col2:
            #países que possuem a maior quantidade de tipos de culinária distintos
            st.markdown('Quantidade de Restaurantes por País')
            dfaux = df.loc[:, ['country_code','cuisines']].groupby('country_code').count().reset_index().sort_values('country_code', ascending=True)
            dfaux.columns = ['country_code', 'cuisines']
            
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='cuisines',labels={'country_code':'Países',
                                                                                 'cuisines':'Quantidade de Culinárias Distintas'}), use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            #quantidade de avaliações feitas por país
            st.markdown('Quantidade de Avaliações por País')
            dfaux = df.loc[:, ['country_code','votes']].groupby('country_code').sum().reset_index().sort_values('votes', ascending=False)
            dfaux.columns = ['country_code', 'votes']
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='votes',labels={'country_code':'Países',
                                                                                       'votes':'Quantidade de Avaliações'}), use_container_width=True)
    
        with col2:
            #maior quantidade de restaurantes que fazem entrega
            st.markdown('Quantidade de Restaurantes que Fazem Entrega por País')
            linhas = df['has_online_delivery'] != 0
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['country_code','has_online_delivery']].groupby('country_code').count().reset_index().sort_values('has_online_delivery',
                                                                                                                                 ascending=False)
            dfaux.columns = ['country_code', 'has_online_delivery']
            
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='has_online_delivery',
                                   labels={'country_code':'Países',
                                           'has_online_delivery':'Quantidade de Restaurantes que Fazem Entrega'}),use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------

    with st.container():
            #quantidade de restaurantes que aceitam reservas
            st.markdown('Quantidade de Restaurantes que Fazem Reserva por País')
            linhas = df['has_table_booking'] != 0
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['country_code','has_table_booking']].groupby('country_code').count().reset_index().sort_values('has_table_booking',
                                                                                                                               ascending=False)
            dfaux.columns = ['country_code', 'has_table_booking']
            
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='country_code', y='has_table_booking',labels={'country_code':'Países',
                                            'has_table_booking':'Quantidade de Restaurantes'}), use_container_width=True)


#==========================================================================================================================================================
#                                                                  Tab 3 - visão Gerencial
#==========================================================================================================================================================


#9. Qual o nome do país que possui, na média, a maior nota média registrada? gráfico de linhas
#10. Qual o nome do país que possui, na média, a menor nota média registrada? gráfico de linhas

with tab3:
    with st.container():
       
        #Países que possuem na média, a maior nota média registrada         
        st.markdown('Países que Possuem a Maior Nota Média de Avaliações de Restaurantes')
        dfaux = df.loc[:, ['country_code', 'aggregate_rating']].groupby('country_code').mean().sort_values('aggregate_rating', ascending=False)
        dfaux = dfaux.rename(columns={'aggregate_rating': 'média_aggregate_rating'})
        dfaux = pd.DataFrame({'country_code': dfaux.index, 'média_aggregate_rating': dfaux['média_aggregate_rating']})
        dfaux.columns = ['country_code', 'média_aggregate_rating']
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='country_code', y='média_aggregate_rating',labels={'country_code':'Países',
                                        'média_aggregate_rating':'Maior nota de Avaliação de Restaurantes'}), use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------

    with st.container():
        #Países que possuem na média, a menor nota média registrada
        st.markdown('Países que Possuem a Menor Nota Média de Avaliações de Restaurantes')
        dfaux = df.loc[:, ['country_code', 'aggregate_rating']].groupby('country_code').mean().sort_values('aggregate_rating', ascending=False)
        dfaux = dfaux.rename(columns={'aggregate_rating': 'média_aggregate_rating'})
        dfaux = pd.DataFrame({'country_code': dfaux.index, 'média_aggregate_rating': dfaux['média_aggregate_rating']})
        dfaux.columns = ['country_code', 'média_aggregate_rating']
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='country_code', y='média_aggregate_rating',labels={'country_code':'Países',                                                                                    'média_aggregate_rating':'Menor nota de Avaliação de Restaurantes'}),use_container_width=True)
    
        
            

