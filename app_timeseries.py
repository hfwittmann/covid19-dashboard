# %%
import streamlit as st
import pandas as pd

from sub.plot_timeseries_helper import get_ts_norm
from sub.plot_timeseries import plotTimeseries

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


def covid19_timeseries(config, S):

    st.markdown('Covid 19 Timeseries Visualization')

    # S.get_set_multiselection(widget=st.sidebar.multiselect,
    #                          name='Countries',
    #                          label='Select Countries',
    #                          options=DD['Confirmed'].country.unique().tolist(),
    #                          default_choices=['Germany', 'United States'])

    LogScale = True
    DD = S.session_state.D
    AbsDiffRate = S['AbsDiffRate'][0]
    n = S['n']

    datecode = sorted(DD['Confirmed'].date.dt.strftime(
        config['DateFormatList']).unique())[-1]

    typeCriterion = 'Deaths'  #

    # calculate from Confirmed

    # add information of shifted confirmed timeshifts to [ 'Confirmed', 'Deaths']

    DD_T_norm = get_DD_T_norm(S['n'], typeCriterion, config, DD).copy()

    # Limit to countries with more than n confirmed cases
    contry_index = DD_T_norm[typeCriterion].groupby(['country'
                                                     ])['Absolute'].max() > n
    countries_with_enough_confirmed_cases = list(
        contry_index[contry_index].index)

    countries_selected = countries_with_enough_confirmed_cases

    # print(S['Countries']), print(countries_selected)
    # print(list(set(S['Countries']) & set(countries_selected)))
    countries_selected = list(set(S['Countries']) & set(countries_selected))

    # func=lambda _: pd.to_datetime('today').strftime("%Y-%m-%d")

    show_projection = False

    timehorizon = 10
    show_details = False

    # if AbsDiffRate == 'Absolute':

    st.markdown("""
    # COVID 19 Timeseries Visualization
    """)

    st.markdown(f""" ... as of {datecode}
    """)
    for type in S['ConfirmedDeaths']:

        fig = plotTimeseries(config=config,
                             z=DD_T_norm[type],
                             AbsDiffRate=AbsDiffRate,
                             type=type,
                             typeCriterion=typeCriterion,
                             LogScale=True,
                             countries=countries_selected,
                             n=n,
                             timehorizon=timehorizon)

        fig.update_layout(legend=dict(yanchor="bottom", xanchor="right"))

        st.plotly_chart(fig, use_container_width=True)