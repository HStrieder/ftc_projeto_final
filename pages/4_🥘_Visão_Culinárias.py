#==========================================================================================================================================================
#bibliotecas
#==========================================================================================================================================================

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

st.set_page_config(page_title='Visão Culinárias', page_icon='🥘', layout='wide')

#==========================================================================================================================================================
#TRANSFORMAÇÕES
#==========================================================================================================================================================

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

#==========================================================================================================================================================

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
    
#==========================================================================================================================================================

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

#==========================================================================================================================================================
#LAYOUT STREAMLIT - Barra Lateral
#==========================================================================================================================================================

st.title('🥘 Visão Culinárias')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

#==========================================================================================================================================================
#Filtro de Países
#==========================================================================================================================================================

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

#==========================================================================================================================================================
#Filtro de Culinária
#==========================================================================================================================================================

culinary_options = st.sidebar.multiselect(
    'Escolha os Tipos de Culinária',
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'California', 'Others',
       'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian',
       'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan',
       'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian',
       'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç'],
    default=['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak'])

linhas_selecionadas = df['cuisines'].isin(culinary_options)
df = df.loc[linhas_selecionadas, :]

#==========================================================================================================================================================
#                            Final - Barra Lateral
#==========================================================================================================================================================

st.sidebar.markdown("""---""")
st.sidebar.write('### Powered by [Strieder](https://www.linkedin.com/in/henrique-strieder/)')


#==========================================================================================================================================================
#                            Layout no Streamlit
#==========================================================================================================================================================

#Tipos de Culinária

#1. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a maior média de avaliação?
#2. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a menor média de avaliação?

#3. Dos restaurantes que possuem o tipo de culinária americana, qual o nome do restaurante com a maior média de avaliação?
#4. Dos restaurantes que possuem o tipo de culinária americana, qual o nome do restaurante com a menor média de avaliação?

#5. Dos restaurantes que possuem o tipo de culinária árabe, qual o nome do restaurante com a maior média de avaliação?
#6. Dos restaurantes que possuem o tipo de culinária árabe, qual o nome do restaurante com a menor média de avaliação?

#7. Dos restaurantes que possuem o tipo de culinária japonesa, qual o nome do restaurante com a maior média de avaliação?
#8. Dos restaurantes que possuem o tipo de culinária japonesa, qual o nome do restaurante com a menor média de avaliação?

#9. Dos restaurantes que possuem o tipo de culinária caseira, qual o nome do restaurante com a maior média de avaliação?
#10. Dos restaurantes que possuem o tipo de culinária caseira, qual o nome do restaurante com a menor média de avaliação?

#11. Qual o tipo de culinária que possui o maior valor médio de um prato para duas pessoas?
#12. Qual o tipo de culinária que possui a maior nota média?
#13. Qual o tipo de culinária que possui mais restaurantes que aceitam pedidos online e fazem entregas?

tab1, tab2 = st.tabs(['Visão Geral', 'Visão Tática'])

#==========================================================================================================================================================
#                                                                  Tab 1 - visão 
#==========================================================================================================================================================

with tab1:
    
    with st.container():
                
        col1,col2 = st.columns(2 , gap='large')
        
        with col1:
            #1. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a maior média de avaliação?
            st.markdown('Restaurantes de Comida Italiana que possuem Maior Avaliação Média')
            linhas = df['cuisines'] == 'Italian'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=False)
            st.dataframe(df_aux)
        
        with col2:
            #2. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a menor média de avaliação?
            st.markdown('Restaurantes de Comida Italiana que possuem Menor Avaliação Média')
            linhas = df['cuisines'] == 'Italian'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=True)
            st.dataframe(df_aux)
        
#-------------------------------------------------------------------------------------------------------------------------------------------------
    with st.container():  
        
        col1, col2 = st.columns(2)   
        
        with col1:
            #3. Dos restaurantes que possuem o tipo de culinária americana, qual o nome do restaurante com a maior média de avaliação?
            st.markdown('Restaurantes de Culinária Americana que Possuem Maior nota média de Avaliação')
            linhas = df['cuisines'] == 'American'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=False)
            st.dataframe(df_aux)

        with col2:
            #4. Dos restaurantes que possuem o tipo de culinária americana, qual o nome do restaurante com a menor média de avaliação?
            st.markdown('Restaurantes de Culinária Americana que Possuem Menor nota média de Avaliação')
            linhas = df['cuisines'] == 'American'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating', 
                                                                                                                                    ascending=True)
            st.dataframe(df_aux)
            
#-------------------------------------------------------------------------------------------------------------------------------------------------
    with st.container():  
        
        col1, col2 = st.columns(2)   
        
        with col1:
            #5. Dos restaurantes que possuem o tipo de culinária árabe, qual o nome do restaurante com a maior média de avaliação?
            st.markdown('Restaurantes de Culinária Árabe que Possuem Maior nota média de Avaliação')
            linhas = df['cuisines'] == 'Arabian'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating', 
                                                                                                                                    ascending=False)
            st.dataframe(df_aux)
            
        with col2:
            #6. Dos restaurantes que possuem o tipo de culinária árabe, qual o nome do restaurante com a menor média de avaliação?
            st.markdown('Restaurantes de Culinária Árabe que Possuem Menor nota média de Avaliação')
            linhas = df['cuisines'] == 'Arabian'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=True)
            st.dataframe(df_aux)

#-------------------------------------------------------------------------------------------------------------------------------------------------
    with st.container():  
        
        col1, col2 = st.columns(2)   
        
        with col1:
            #7. Dos restaurantes que possuem o tipo de culinária japonesa, qual o nome do restaurante com a maior média de avaliação?
            st.markdown('Restaurantes de Culinária Japonesa que Possuem Maior nota média de Avaliação')
            linhas = df['cuisines'] == 'Japanese'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=False)
            st.dataframe(df_aux)
            
        with col2:
            #8. Dos restaurantes que possuem o tipo de culinária japonesa, qual o nome do restaurante com a menor média de avaliação?
            st.markdown('Restaurantes de Culinária Japonesa que Possuem Menor nota média de Avaliação')
            linhas = df['cuisines'] == 'Japanese'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=True)
            st.dataframe(df_aux)
            
#-------------------------------------------------------------------------------------------------------------------------------------------------
    with st.container():  
        
        col1, col2 = st.columns(2)   
        
        with col1:
            #9. Dos restaurantes que possuem o tipo de culinária caseira, qual o nome do restaurante com a maior média de avaliação?
            st.markdown('Restaurantes de Culinária Caseira que Possuem Maior nota média de Avaliação')
            linhas = df['cuisines'] == 'Home-made'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=False)
            st.dataframe(df_aux)
            
        with col2:
            #10. Dos restaurantes que possuem o tipo de culinária caseira, qual o nome do restaurante com a menor média de avaliação?
            st.markdown('Restaurantes de Culinária Caseira que Possuem Menor nota média de Avaliação')
            linhas = df['cuisines'] == 'Home-made'
            df1 = df.loc[linhas,:].copy()
            df_aux = df1.loc[:, ['restaurant_name','aggregate_rating']].groupby('restaurant_name').mean().reset_index().sort_values('aggregate_rating',
                                                                                                                                    ascending=True)
            st.dataframe(df_aux)
            
#==========================================================================================================================================================
#                                                                  Tab 2 - visão Tática
#==========================================================================================================================================================

#11. Qual o tipo de culinária que possui o maior valor médio de um prato para duas pessoas?
#12. Qual o tipo de culinária que possui a maior nota média?
#13. Qual o tipo de culinária que possui mais restaurantes que aceitam pedidos online e fazem entregas?

with tab2:
    with st.container():
                
        #11. Qual o tipo de culinária que possui o maior valor médio de um prato para duas pessoas?
        st.markdown('Valor Médio para Refeição para Duas Pessoas com Custo Mais Alto por Culinárias')
        dfaux = df.loc[:, ['cuisines','average_cost_for_two']].groupby('cuisines').mean().reset_index().sort_values('average_cost_for_two', ascending=False)
        
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='cuisines', y='average_cost_for_two',labels={'cuisines':'Culinárias',
                                                                 'average_cost_for_two':'Valor de Uma Refeição para Dois'}), use_container_width=True)
    

#-------------------------------------------------------------------------------------------------------------------------------------------------
            
    with st.container():
        
        #12. Qual o tipo de culinária que possui a maior nota média?
        st.markdown('Nota média Mais Alta das Culinárias')
        dfaux = df.loc[:, ['cuisines','aggregate_rating']].groupby('cuisines').mean().reset_index().sort_values('aggregate_rating', ascending=False)
        
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='cuisines', y='aggregate_rating',labels={'cuisines':'Culinárias',
                                                                 'aggregate_rating':'Nota'}), use_container_width=True)
    
    
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    with st.container():        
        
        #13. Qual o tipo de culinária que possui mais restaurantes que aceitam pedidos online e fazem entregas?
        st.markdown('Culinárias que Possuem mais Restaurantes que Aceitam Pedidos Online e Fazem Entregas')
        linhas = df['has_online_delivery'] != 0 
        df1 = df.loc[linhas,:].copy()
        dfaux = df1.loc[:, ['cuisines','restaurant_name']].groupby('cuisines').count().reset_index().sort_values('restaurant_name', ascending=False)
        
        # gráfico
        st.plotly_chart(px.bar(dfaux, x='cuisines', y='restaurant_name',labels={'cuisines':'Culinárias',
                                                                 'restaurant_name':'Quantidade de Restaurantes'}), use_container_width=True)
            
        
            