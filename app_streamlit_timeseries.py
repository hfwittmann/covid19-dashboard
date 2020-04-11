# %%
import streamlit as st
import pandas as pd
import numpy as np
import yaml

import plotly.graph_objects as go
import plotly.express as px

from sub.mydata_change import load_timeseries_change
from sub.myplot import plotMap
from sub.plot_timeseries_helper import get_ts_norm
from sub.plot_timeseries import plotTimeseries
from sub.projection_helper import plot_cases_plus
from sub.fancy_cache import fancy_cache


@fancy_cache(ttl=86400 / 4, unique_to_session=False, persist=True)
def get_DD_T_norm(n, typeCriterion, config, DD):
    '''
    n is the number of cases to define T_0
    '''
    # calculate timeshifts
    T_norm = get_ts_norm(config, DD[typeCriterion], n).set_index(
        ['date', 'country'])[['T_norm', 'T_0', 'country_T_0', 'T_norm_days']]

    DD_T_norm = dict()

    for type in ['Confirmed', 'Death_Rate', 'Deaths']:

        DD[type] = DD[type].set_index(['date', 'country'])

        DD_T_norm[type] = pd.merge(left=DD[type],
                                   right=T_norm,
                                   left_index=True,
                                   right_index=True)

        DD_T_norm[type].reset_index(inplace=True)

    return DD_T_norm


def covid19_timeseries(config, DD):

    ######################################### Controls ##############################################
    ConfirmedDeaths = st.sidebar.multiselect(
        'Select Type', ['Confirmed', 'Deaths', 'Death_Rate'],
        default=['Confirmed', 'Deaths'])
    LogScale = True  # st.sidebar.selectbox('Select Log Scale', options=[True, False])

    datecode = sorted(DD['Confirmed'].date.dt.strftime(
        config['DateFormatList']).unique())[-1]

    AbsDiffRate = st.sidebar.selectbox(
        'Absolute, Difference per Day, or Change(%) per Day',
        ['Absolute', 'Difference', 'Change(%)'])

    if AbsDiffRate == 'Change(%)':
        st.sidebar.markdown(
            '*Remark: The Change(%) is averaged over the previous 3 days*')
    #     print()
    #     Averaging_Period = st.sidebar.slider(
    #         'Change(%) Averaging Period (Days)',
    #         min_value=1,
    #         max_value=5,
    #         value=3)

    #     for type in ConfirmedDeaths:
    #         DD[type]['Change(%)'] = DD[type][f'Change(%)_{Averaging_Period}']

    st.sidebar.header("Define day zero")
    typeCriterion = 'Deaths'
    # typeCriterion = st.sidebar.selectbox(
    #     'Select reported type to define the day zero', ['Confirmed', 'Deaths'])

    if typeCriterion in ['Deaths']:
        n = st.sidebar.selectbox(
            'Select Number of deaths to define the day zero, ie the day when the number of deaths in a country hit that number.',
            options=[300, 500, 700],
            index=0,
            key='Deaths')

    if typeCriterion in ['Confirmed']:
        n = st.sidebar.slider(
            'Select Number of confirmed cases to define the day zero, ie the day when the number of confirmed cases in a country hit that number.',
            1000,
            10000,
            value=5000,
            step=1000,
            key='Confirmed')

    # calculate from Confirmed

    # add information of shifted confirmed timeshifts to [ 'Confirmed', 'Deaths']

    DD_T_norm = get_DD_T_norm(n, typeCriterion, config, DD).copy()

    # Limit to countries with more than n confirmed cases
    contry_index = DD_T_norm[typeCriterion].groupby(['country'
                                                     ])['Absolute'].max() > n
    countries_with_enough_confirmed_cases = list(
        contry_index[contry_index].index)

    countries_selected = countries_with_enough_confirmed_cases

    # func=lambda _: pd.to_datetime('today').strftime("%Y-%m-%d")

    projection = st.sidebar.empty()
    show_projection = st.sidebar.empty()

    timehorizon = 10
    show_details = False

    # if AbsDiffRate == 'Absolute':

    projection = projection.header("Projection")

    show_projection = show_projection.radio('Show projection', [False, True],
                                            key='show_projection')

    if show_projection:
        timehorizon = st.sidebar.selectbox('Select timehorizon', [10, 20, 30])
        show_details = st.sidebar.radio('Show details of prediction model',
                                        [False, True])

    # countries_selected = st.sidebar.multiselect(
    #     'Select Country',
    #     countries_with_enough_confirmed_cases,
    #     default=countries_with_enough_confirmed_cases)

    if show_details:

        st.markdown("""
        # COVID 19 Timeseries Prediction Model
        """)
        st.markdown(
            f'''## *Remark: The model uses the prediction of the relative change rate for the forecast.*  \n
            ''')
        st.markdown(f'''For each country it proceeds like this:  \n

        - For each country:
        -- The point in time T_0 where the number of deaths is ~ {n} is established
        -- A new time variable is introduced, TNorm, ie the number of days before and after T_0
        ''')

        st.markdown(f''' Now the data are split into  \n
        - country (eg Germany) and
        - ex-country (eg all the other countries except for Germany)
        ''')

        st.markdown(
            f''' Then for the ex-country for each Tnorm day the mean and std are fitted.'''
        )
        st.markdown(
            f''' To simplify further, subsequently only the average of the stds is used'''
        )

        st.markdown(f''' So now we have std_ex and mean_ex = f(Tnorm) ''')

        st.markdown(
            f''' Subsequently for the country (eg Germany) data, the relative change rate is calculated as a function of TNorm'''
        )

        st.markdown(
            f''' For the one day forecast, the next day is calulated, by  \n
        - first calculating today's quantile (using std_ex and  mean_x(TNorm)
        - and the plugging it into and then plugging it into tomorrow's distribution (using std_ex and  mean_x(TNorm+1) '''
        )

        st.markdown(
            f''' For longer term forecasts this is done in a walk-forward fashion '''
        )

    ######################################### Plotting ##############################################
    else:
        st.markdown("""
        # COVID 19 Timeseries Visualization
        """)

        st.markdown(f""" ... as of {datecode}
        """)
        for type in ConfirmedDeaths:

            fig = plotTimeseries(config=config,
                                 show_projection=show_projection,
                                 z=DD_T_norm[type],
                                 AbsDiffRate=AbsDiffRate,
                                 type=type,
                                 typeCriterion=typeCriterion,
                                 LogScale=True,
                                 countries=countries_selected,
                                 n=n,
                                 timehorizon=timehorizon)

            st.plotly_chart(fig)
