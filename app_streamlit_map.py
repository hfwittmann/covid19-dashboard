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

from sub.helper import get_set_selection, get_set_multiselection


def covid19_maps(config, DD):

    st.markdown("""
    # COVID 19 Map Visualization""")

    # print(sorted(DD['Confirmed'].index))
    # print(sorted(DD['Confirmed'].columns))

    options_date_map = sorted(DD['Confirmed'].date.dt.strftime(
        config['DateFormatList']).unique(),
                              reverse=True)
    # print(options_date_map)

    ######################################### Controls ##############################################
    ConfirmedDeaths = get_set_multiselection(
        st.sidebar.multiselect,
        name='ConfirmedDeaths',
        label='Select Type',
        options=['Death_Rate', 'Confirmed', 'Deaths'],
        default_choices=['Confirmed', 'Deaths'])

    LogScale = True  # st.sidebar.selectbox('Select Log Scale', options=[True, False])

    datecode = st.sidebar.selectbox("Select Date",
                                    options=list(options_date_map))

    st.markdown(f""" ... as of {datecode}
    """)

    AbsDiffRate = get_set_selection(
        st.sidebar.selectbox,
        name='AbsDiffRate',
        label='Absolute, Difference per Day, or Change(%) per Day',
        options=['Absolute', 'Difference', 'Change(%)'])

    if AbsDiffRate == 'Change(%)':
        st.sidebar.markdown(
            '*Remark: The Change(%) is averaged over the previous 3 days*')
    #     Averaging_Period = st.sidebar.slider(
    #         'Change(%) Averaging Period (Days)',
    #         min_value=1,
    #         max_value=5,
    #         value=3)

    # for type in ConfirmedDeaths:
    #     DD[type]['Change(%)'] = DD[type][f'Change(%)_{Averaging_Period}']

    # color_continuous_scale = st.sidebar.selectbox(
    #     'Select Color Scale:', options=px.colors.typed_colorscales())
    Color_continous_scale = config['Color_continous_scale']

    # reverse_color = st.sidebar.selectbox('Reverse color scale:', [False, True])
    Reverse_colors = config['Reverse_colors']

    ######################################### Plotting ##############################################
    for type in ConfirmedDeaths:

        D = DD[type]
        color_continuous_scale = Color_continous_scale[AbsDiffRate][type]
        reverse_color = Reverse_colors[AbsDiffRate][type]

        D_selection = D.loc[D.date == datecode]

        # print(D_selection.loc[D_selection.country == 'Germany'])

        fig = plotMap(z=D_selection,
                      type=type,
                      AbsDiffRate=AbsDiffRate,
                      LogScale=LogScale,
                      datecode=datecode,
                      color_continuous_scale=color_continuous_scale,
                      reverse_color=color_continuous_scale,
                      config=config)

        st.plotly_chart(fig)

    return None