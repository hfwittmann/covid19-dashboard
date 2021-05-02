from datetime import date
import json
import plotly
from re import sub
from plotly import graph_objects as go

import pandas as pd
import streamlit as st
import yaml

from subs.access_backend import get_countries
from subs.access_backend import get_data
# from subs.access_backend import get_plot
from subs.getPlots import getPlot

st.set_page_config(layout='wide')

from nav_sub import SessionState
from nav_sub.settings import Settings

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
with open('navigation_covid19.yaml', 'r') as f:
    tree = yaml.safe_load(f)

query_params = st.experimental_get_query_params()

T = dict()
_, countries = get_countries()
_, T['Confirmed'] = get_data('Confirmed')
_, T['Death'] = get_data('Death')


countries['GDP/capita'] = countries['GDP (BILLIONS)']/countries['Population(1 July 2019)']

for type in ['Death', 'Confirmed']:
    T[type] = pd.merge(T[type], countries, left_on=['country'], right_on=['COUNTRY'])
    T[type]['7d_per_100000'] = T[type]['7d']*7*100000/T[type]['Population(1 July 2019)']


options_date_map = sorted(T['Confirmed']['date'].unique(), reverse=True)

session_state = SessionState.get(first_query_params=query_params,
                                 countries=countries,
                                 tree=tree,
                                 options_date_map=options_date_map)

S = Settings(session_state)

##################################################################################################################################
from nav_sub.github_icon import github_forkme

st.markdown(github_forkme, unsafe_allow_html=True)
##################################################################################################################################

st.sidebar.markdown("""
# COVID 19 Visualization
This visualisation presents maps and timeseries of the current corona virus pandemic.
""")

S.place_widget('Visualisation')
S.place_widget('ConfirmedDeath')

S.place_widget('Countries')
# S.place_widget('Differences')
# S.place_widget('AbsDiffRate')

if S['Visualisation'] in ['Timeseries']:
    st.sidebar.header("Define day zero")
S.place_widget('Day_Zero')
S.place_widget('Date')

# if S['AbsDiffRate'] == 'Change(%)':
#     st.sidebar.markdown(
#         '*Remark: The Change(%) is averaged over the previous 3 days*')

# # %%
# if S['Visualisation'] == 'Maps':
#     covid19_maps(config, S)


if S['Visualisation'] == 'Timeseries':

    if len(S['Countries']) > 0:

        for type in ['Death', 'Confirmed']:

            if  type in S['ConfirmedDeath']:

                c1, _, c2 = st.beta_columns((10, 1, 10))

                for c, diff in zip((c1, c2), ['7d_per_100000', 'trend']):

                    c.write(type + ' ' + diff)
                    timeseries = T[type]
                    timeseries_selection = timeseries[timeseries.country.isin(
                        S['Countries'])]

                    _ = getPlot('timeseries',
                                timeseries_selection,
                                diff,
                                None,
                                config=config)
                    fig = _['plot']

                    c.plotly_chart(fig, use_container_width=True)
                #covid19_timeseries(config, S)

                # _ = getPlot('timeseries', timeseries_selection, 'cases', None, config=config)
                # fig = _['plot']

                # st.plotly_chart(fig, use_container_width=True)

if S['Visualisation'] == 'Maps' and type in S['ConfirmedDeath']:

    for type in ['Death', 'Confirmed']:
        st.write(type)
        timeseries = T[type]

        chosendate = S['Datecode']
        mapdata= timeseries[timeseries.date.isin([chosendate])].set_index('country')

        _ = getPlot('map',
                    mapdata,
                    '7d_per_100000',
                    None,
                    config=config)
        fig = _['plot']
        st.plotly_chart(fig, use_container_width=True)