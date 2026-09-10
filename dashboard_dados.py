import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh


tabela = pd.read_json('https://raw.githubusercontent.com/kelsarata2-create/coletor-trafego-aereo-sul/main/voos_sul_atual.json')
tabela = tabela[tabela['Callsign'] != '']
tabela = tabela[tabela['Speed(kt)'] != 'Sem dados']
tabela['Speed(kt)'] = tabela['Speed(kt)'].str.replace('kt', '').astype(int)
tabela['Speed'] = tabela['Speed(kt)'].astype(str) + ' kt'

if 'Flight level' in tabela.columns:
    tabela = tabela[tabela['Flight level'] != 'Sem dados']
    tabela['FL_numerico'] = tabela['Flight level'].str.replace('FL', '').astype(float) * 100

if 'Altitude' in tabela.columns:
    tabela = tabela[tabela['Altitude'] != 'Sem dados']
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

st_autorefresh(120000)
st.set_page_config(page_title='FLIGHT MAPPING', page_icon='✈️', layout="wide")
st.markdown("<h1 style='text-align: center;'>FLIGHT MAPPING</h1>", unsafe_allow_html=True)

tab, mapa = st.tabs(['INFORMATION'.center(101), 'CURRENT POSITION'.center(105)])

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
    st.dataframe(tabela.drop(columns=['Altitude_calculo', 'Speed(kt)']), hide_index=True, height=501)

with mapa:
    dynamic_max = tabela['Altitude_calculo'].max()
    dynamic_min = tabela['Altitude_calculo'].min()
    dynamic_mean = int(tabela['Altitude_calculo'].mean())
    altitude_selecionada = st.slider("SELECT ALTITUDE", dynamic_min, dynamic_max, dynamic_mean, step=1000)
    tabela_mapa = tabela[tabela['Altitude_calculo'] <= altitude_selecionada]

    center = {'lat': media_lat, 'lon': media_lon}
    fig = px.scatter_map(
        data_frame=tabela_mapa,
        lat='Latitude',
        lon='Longitude',
        center=center,
        hover_name='Callsign',
        hover_data=['Altitude/Flight level'],
        zoom=5,
        map_style="open-street-map",
    )
    fig.update_traces(marker=dict(size=10, color='red'))
    st.plotly_chart(fig, use_container_width=True, height=509)