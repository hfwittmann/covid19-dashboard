import json
import plotly
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

from subs.access_backend import get_countries
from subs.colors import rgba_to_rgb
from subs.colors import get_countries_colors

@st.cache(allow_output_mutation=True)
def map_plot(mapdata, y, mydate, config):

    #print(y)
    assert y in ['cases', '7d_per_100000', 'trend'], f'{y}'

    color_continuous_scale = config['Color_continous_scale']

    # colorrange = config['Override_ColorRanges'][AbsDiffRate][type]

    # if colorrange != {}:
    #     colorrange['range_color'] = tuple(colorrange['range_color'])

    # fig = px.choropleth(

    # )

    thisplot = px.choropleth(mapdata,
                             locations='CODE_x',
                             scope='world',
                             hover_name='COUNTRY',
                             color=y)
    #     height=400,)

    thisplot.update_layout(
        # title_text=f'<b>{TYPES[type]}</b>',
        geo=dict(showframe=False,
                 showcoastlines=False,
                 projection_type='equirectangular'),
        annotations=[
            dict(
                x=0.55,
                y=0.1,
                xref='paper',
                yref='paper',
                text=
                'Source: <a href="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series">\
            Johns Hopkins CSSE</a>',
                showarrow=False)
        ])

    fig_performance = dict(data=thisplot.data, layout=thisplot.layout)

    return fig_performance

@st.cache(allow_output_mutation=True)
def timeseries_plot(timeseries_data, y, mydate, config):

    # print(y)
    assert y in [
        'cases', 'diffs', '1d', '7d', '28d', 'trend', '7d_per_100000'
    ], f'{y}'

    countries_colors = get_countries_colors(config)
    country_color_marker = countries_colors.set_index(
        'country')['country_color_marker'].to_dict()

    country_color_marker_line = countries_colors.set_index(
        'country')['country_color_marker_line'].to_dict()

    country_number_mod = countries_colors.set_index(
        'country')['country_number_mod'].to_dict()

    timeseries_data = pd.merge(timeseries_data,
                               countries_colors,
                               on=["country"])

    thisplot = px.scatter(timeseries_data,
                          x='date',
                          y=y,
                          color='country',
                          color_discrete_map=country_color_marker,
                          hover_data=['date', 'T0'],
                          log_y=True)

    def blub(trace):
        name = trace['name']

        return trace.update(
            marker_line=dict(width=1, color=country_color_marker_line[name]))

    # thisplot.update_traces()
    # fig.for_each_trace(lambda trace: trace.update(marker=dict(symbol=10))
    thisplot.for_each_trace(lambda trace: blub(trace))

    fig_performance = dict(data=thisplot.data, layout=thisplot.layout)

    return fig_performance


def getPlot(plottype, timeseries_data, y, status, mydate, config):

    plots = {
        'timeseries': timeseries_plot,
        'map': map_plot
        # 'maps
    }

    return {
        'status': status,
        'plot': plots[plottype](timeseries_data, y, mydate, config)
    }
