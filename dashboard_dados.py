import glob
import os
import pandas as pd
import streamlit as st
import plotly.express as px

procura_arquivo = glob.glob(
    '../coletor-trafego-aereo-sul/voos_sul_*.json')

arquivo_mais_recente = max(procura_arquivo, key=os.path.getmtime)

tabela = pd.read_json(arquivo_mais_recente)
tabela = tabela[tabela['Callsign'] != '']
tabela = tabela[tabela['Speed(kt)'] != 'Sem dados']
tabela['Speed(kt)'] = tabela['Speed(kt)'].str.replace('kt', '').astype(int)

if 'Flight level' in tabela.columns:
    tabela['FL_numerico'] = tabela['Flight level'].str.replace('FL', '').astype(float) * 100

if 'Altitude' in tabela.columns:
    tabela['Altitude_numerica'] = tabela['Altitude'].str.replace('ft', '').astype(float)

if 'Altitude' in tabela.columns and 'Flight level' in tabela.columns:
    tabela['Altitude/Flight level'] = tabela['Altitude'].fillna(tabela['Flight level'])
    tabela['Altitude_calculo'] = tabela['Altitude_numerica'].fillna(tabela['FL_numerico'])
elif 'Altitude' in tabela.columns:
    tabela['Altitude/Flight level'] = tabela['Altitude']
    tabela['Altitude_calculo'] = tabela['Altitude_numerica']
else:
    tabela['Altitude/Flight level'] = tabela['Flight level']
    tabela['Altitude_calculo'] = tabela['FL_numerico']

tabela = tabela[tabela['Altitude/Flight level'] != 'Sem dados']
tabela['Altitude_calculo'] = tabela['Altitude_calculo'].astype(int)
tabela.drop(['Flight level', 'Altitude', 'FL_numerico', 'Altitude_numerica'], axis=1, inplace=True, errors='ignore')

aero_total = len(tabela)
media_lat = tabela['Latitude'].mean()
media_lon = tabela['Longitude'].mean()
max_speed = max(tabela['Speed(kt)'])
max_altitude = max(tabela['Altitude_calculo'])
max_companies = tabela['Origin'].mode().max()

st.set_page_config(page_title='AERIAL MAPPING', page_icon='✈️', layout="wide")
st.title('AERIAL MAPPING')

tab, mapa = st.tabs(['INFORMATION', 'CURRENT POSITION'])

with tab:
    aero_detectadas, altitude_max, velocidade_max, max_companhias = st.columns(4)
    with aero_detectadas:
        st.metric(label='DETECTED AIRCRAFTS', value=aero_total)
    with velocidade_max:
        st.metric(label='MAX SPEED (kt)', value=max_speed)
    with altitude_max:
        st.metric(label='MAX ALTITUDE (ft)', value=max_altitude)
    with max_companhias:
        st.metric(label='MOST COMPANIES', value=max_companies)
    st.dataframe(tabela.drop(columns=['Altitude_calculo']))

with mapa:
    center = {'lat': media_lat, 'lon': media_lon}
    fig = px.scatter_map(
        data_frame=tabela,
        lat='Latitude',
        lon='Longitude',
        center=center,
        hover_name='Callsign',
        hover_data=['Altitude/Flight level'],
        zoom=5,
        map_style="open-street-map",
    )
    st.plotly_chart(fig)


""" APAGAR INDICES
    COLOCAR KT NA COLUNA SPEED
    REAJUSTAR MAPA
    AUMENTAR BOLINHA E TROCAR COR DAS BOLINHAS
    ACRESCENTAR SUGERIDO PELO CLAUDE"""