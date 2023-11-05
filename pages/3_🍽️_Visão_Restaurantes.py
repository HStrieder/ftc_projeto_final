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

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

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

st.title('🍽️ Visão Restaurantes')
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

#1. Qual o nome do restaurante que possui a maior quantidade de avaliações?
#2. Qual o nome do restaurante com a maior nota média?
#3. Qual o nome do restaurante que possui o maior valor de uma prato para duas pessoas?
#4. Qual o nome do restaurante de tipo de culinária brasileira que possui a menor média de avaliação?
#5. Qual o nome do restaurante de tipo de culinária brasileira, e que é do Brasil, que possui a maior média de avaliação?

#6. Os restaurantes que aceitam pedido online são também, na média, os restaurantes que mais possuem avaliações registradas?
#7. Os restaurantes que fazem reservas são também, na média, os restaurantes que possuem o maior valor médio de um prato para duas pessoas?
#8. Os restaurantes do tipo de culinária japonesa dos Estados Unidos da América possuem
# um valor médio de prato para duas pessoas maior que as churrascarias americanas (BBQ)?

tab1, tab2 = st.tabs(['Visão Geográfica', 'Visão Tática'])

#==========================================================================================================================================================
#                                                                  Tab 1 - visão Geográfica
#==========================================================================================================================================================

#1. Qual o nome do restaurante que possui a maior quantidade de avaliações?
#2. Qual o nome do restaurante com a maior nota média?
#3. Qual o nome do restaurante que possui o maior valor de uma prato para duas pessoas?
#4. Qual o nome do restaurante de tipo de culinária brasileira que possui a menor média de avaliação?
#5. Qual o nome do restaurante de tipo de culinária brasileira, e que é do Brasil, que possui a maior média de avaliação?,

with tab1:
    
    with st.container():
                
        col1,col2 = st.columns(2 , gap='large')
        
        with col1:
            #Qual o nome do restaurante que possui a maior quantidade de avaliações?           
            st.markdown('Restaurantes com Maior Número de Avaliações')
            dfaux = df.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').count().reset_index().sort_values('aggregate_rating',
                                                                                                                                   ascending=False)
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='aggregate_rating',labels={'restaurant_name':'Restaurantes',
                                                                                'aggregate_rating':'Quantidade de Avaliações'}), use_container_width=True)

        with col2:
            #Qual o nome do restaurante com a maior nota média?
            st.markdown('Restaurantes com a Maior Nota Média')
            dfaux = df.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                ascending=False)
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='aggregate_rating',labels={'restaurant_name':'Restaurantes',
                                                                                'aggregate_rating':'Nota Média'}), use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------
            
    with st.container():   
    
            #Qual o nome do restaurante que possui o maior valor de uma prato para duas pessoas?
            st.markdown('Restaurantes com Refeição para Duas Pessoas Mais Caros')
            dfaux = df.loc[:, ['restaurant_name','average_cost_for_two']].groupby('restaurant_name').mean().reset_index().sort_values('average_cost_for_two',
                                                                                                                                      ascending=False)
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='average_cost_for_two',labels={'restaurant_name':'Restaurantes',
                                                                'average_cost_for_two':'Preço de uma Refeição para Duas Pessoas'}), use_container_width=True)

        
    with st.container():  
        
        col1, col2 = st.columns(2)   
        
        with col1:
            #Qual o nome do restaurante de tipo de culinária brasileira que possui a menor média de avaliação?
            st.markdown('Restaurantes de Culinária Brasileira que Possuem Menor nota média de Avaliação')
            linhas = df['cuisines'] == 'Brazilian'
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=True)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='aggregate_rating',labels={'restaurant_name':'Restaurantes',
                                                      'aggregate_rating':'Nota'}), use_container_width=True)

        with col2:
            #Qual o nome do restaurante de tipo de culinária brasileira, e que é do Brasil, que possui a maior média de avaliação?
            st.markdown('Restaurantes de Culinária Brasileira que Possuem Maior nota média de Avaliação')
            linhas = df['cuisines'] == 'Brazilian'
            df1 = df.loc[linhas,:].copy()
            dfaux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=False)
        
            # gráfico
            st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='aggregate_rating',labels={'restaurant_name':'Restaurantes',
                                                      'aggregate_rating':'Nota'}), use_container_width=True)
            
#==========================================================================================================================================================
#                                                                  Tab 2 - visão Tática
#==========================================================================================================================================================


#6. Os restaurantes que aceitam pedido online são também, na média, os restaurantes que mais possuem avaliações registradas?
#7. Os restaurantes que fazem reservas são também, na média, os restaurantes que possuem o maior valor médio de um prato para duas pessoas?
#8. Os restaurantes do tipo de culinária japonesa dos Estados Unidos da América possuem um valor médio de prato para duas pessoas maior que as churrascarias americanas (BBQ)?

with tab2:
    with st.container():
        
        #Os restaurantes que aceitam pedido online são também, na média, os restaurantes que mais possuem avaliações registradas?
        st.markdown('Quantidade de Votos Restaurantes que Fazem Entregas x Restaurantes que Não Fazem Entregas')
        # Separa os restaurantes que entregam
        restaurantes_com_entrega = df[df['has_online_delivery'] == 1]
        
        # Separa os restaurantes que não entregam
        restaurantes_sem_entrega = df[df['has_online_delivery'] == 0]
        
        # Calcula a quantidade de votos para os restaurantes com entrega
        total_votos_com_entrega = restaurantes_com_entrega['votes'].sum()
        
        # Calcula a quantidade de votos para os restaurantes sem entrega
        total_votos_sem_entrega = restaurantes_sem_entrega['votes'].sum()
        
        data = {'Entrega': ['Fazem Entregas', 'Não Fazem Entregas'], 'Total de Avaliações': [total_votos_com_entrega, total_votos_sem_entrega]}
        df3 = pd.DataFrame(data)

        # Crie o gráfico de barras
        fig = px.bar(df3, x='Entrega', y='Total de Avaliações', labels={'Entrega': 'Tipo de Entrega', 'Total de Avaliações': 'Quantidade de Votos'})
        
        # Exiba o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------
            
    with st.container():
        

        #Os restaurantes que fazem reservas são também, na média, os restaurantes que possuem o maior valor médio de um prato para duas pessoas?
        st.markdown('Valor Médio de Uma Refeição para Duas Pessoas nos Restaurantes que Fazem Reservas')
        linhas = df['has_table_booking'] != 0
        df1 = df.loc[linhas,:].copy()
        dfaux = df1.loc[:, ['restaurant_name','average_cost_for_two']].groupby('restaurant_name').mean().reset_index().sort_values('average_cost_for_two',
                                                                                                                                    ascending=False)
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='restaurant_name', y='average_cost_for_two',labels={'restaurant_name':'Restaurantes',
                                                                 'average_cost_for_two':'Valor de Uma Refeição para Dois'}), use_container_width=True)
    
    
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    with st.container():        
        #Os restaurantes do tipo de culinária japonesa dos Estados Unidos da América possuem um valor médio de prato para duas pessoas maior que as churrascarias americanas (BBQ)?
        st.markdown('Valor Médio dos Restaurantes de Churrasco Americano BBQ x de Comida Japonesa')
        linhas = df['country_code'] == 'United States of America'
        df1 = df.loc[linhas,:].copy()
        df_aux = df1.loc[:, ['cuisines','average_cost_for_two']].groupby('cuisines').mean().reset_index().sort_values('average_cost_for_two',
                                                                                                                          ascending=False)
        df_aux01 = df_aux.loc[df_aux['cuisines'] == 'Japanese', :]
        df_aux02 = df_aux.loc[df_aux['cuisines'] == 'BBQ', :]
        df3 = pd.concat([df_aux01 ,df_aux02]).reset_index()
        st.plotly_chart(px.bar(df3, x='cuisines', y='average_cost_for_two',labels={'cuisines':'Culinárias',
                                                                 'average_cost_for_two':'Valor de Uma Refeição para Dois'}), use_container_width=True)
            
        
            