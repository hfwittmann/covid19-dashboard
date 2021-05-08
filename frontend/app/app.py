from datetime import date
import json
import plotly
from re import sub
from plotly import graph_objects as go

import pandas as pd
import streamlit as st
import yaml

from subs.access_backend import get_countries
from subs.access_backend import get_dates
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

_, dates = get_dates()
options_date_map = sorted(dates['date'].unique(), reverse=True)
lastdate = options_date_map[0]

_, countries = get_countries()
_, T['Confirmed'] = get_data(lastdate, 'Confirmed')
_, T['Death'] = get_data(lastdate, 'Death')


countries['GDP/capita'] = countries['GDP (BILLIONS)']/countries['Population(1 July 2019)']
# st.write(countries)


for mytype in ['Death', 'Confirmed']:
    T[mytype] = pd.merge(T[mytype], countries, left_on=['country'], right_on=['COUNTRY'])
    T[mytype]['7d_per_100000'] = T[mytype]['7d']*7*100000/T[mytype]['Population(1 July 2019)']



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

S.place_widget('Metric')

S.place_widget('Countries')
# S.place_widget('Differences')
# S.place_widget('AbsDiffRate')

# if S['Visualisation'] in ['Timeseries']:
#     st.sidebar.header("Define day zero")
#     S.place_widget('Day_Zero')
S.place_widget('Date')

# if S['AbsDiffRate'] == 'Change(%)':
#     st.sidebar.markdown(
#         '*Remark: The Change(%) is averaged over the previous 3 days*')

# # %%
# if S['Visualisation'] == 'Maps':
#     covid19_maps(config, S)


if S['Visualisation'] == 'Timeseries':

    if len(S['Countries']) > 0:

        for mytype in ['Death', 'Confirmed']:

            if mytype in S['ConfirmedDeath']:

                # c1, _, c2 = st.beta_columns((10, 1, 10))
                # for c, diff in zip((c1, c2), ['7d_per_100000', 'trend']):

                _, c, _ = st.beta_columns((1, 10, 1))

                if S['Metric'] in ['7d_per_100000', 'trend']:

                    diff = S['Metric']
                    c.write(mytype + ' ' + diff)
                    timeseries = T[mytype]
                    timeseries_selection = timeseries[timeseries.country.isin(
                        S['Countries'])]

                    _ = getPlot('timeseries',
                                timeseries_selection,
                                diff,
                                None,
                                lastdate,
                                config=config)
                    fig = _['plot']

                    c.plotly_chart(fig, use_container_width=True)
                #covid19_timeseries(config, S)

                # _ = getPlot('timeseries', timeseries_selection, 'cases', None, config=config)
                # fig = _['plot']

                # st.plotly_chart(fig, use_container_width=True)

if S['Visualisation'] == 'Maps' and mytype in S['ConfirmedDeath']:

    for mytype in ['Death', 'Confirmed']:
        st.write(mytype)
        timeseries = T[mytype]
        dates_str = timeseries.date.apply(lambda x: x.strftime("%Y-%m-%d"))

        chosendate = S['Datecode']
        mapdata=timeseries.loc[dates_str==chosendate]

        if S['Metric'] in ['7d_per_100000', 'trend']:
            _ = getPlot('map',
                        mapdata,
                        S['Metric'],
                        None,
                        chosendate,
                        config=config)
            fig = _['plot']
            st.plotly_chart(fig, use_container_width=True)