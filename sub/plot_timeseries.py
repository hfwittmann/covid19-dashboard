# %%
import streamlit as st
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_integer_dtype

import numpy as np
import re
import plotly
import plotly.express as px

from sub.fancy_cache import fancy_cache


# hash_funcs={
#     pd.DataFrame:
#     lambda _: pd.to_datetime('today').strftime("%Y-%m-%d"),
#     str:
#     lambda x: blubber(x)
# },
def plot_cases_plus(TNORM, type, Types_type, AbsDiffRate):

    TNORM = TNORM.copy()
    TNORM['date'] = TNORM['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    fig = px.scatter(TNORM,
                     x='T_norm_days',
                     y=AbsDiffRate,
                     color='country_T_0',
                     hover_name='country',
                     hover_data=['date'],
                     log_y=True)

    # print(px.colors.qualitative.Plotly)
    ncolors = len(px.colors.qualitative.Plotly)

    # fig.for_each_trace(lambda trace: print(trace.hovertemplate))

    fig.for_each_trace(lambda trace: trace.update(hovertemplate=re.sub(
        pattern='<br>country_T_0=[a-zA-Z0-9 :-]*',
        repl='',
        string=trace.hovertemplate)))

    # print(fig.data[-1])

    return fig


def plotTimeseries(config,
                   z,
                   LogScale,
                   countries,
                   n=500,
                   AbsDiffRate='Absolute',
                   type='Confirmed',
                   typeCriterion='Confirmed',
                   timehorizon=10):

    TYPES = config['TYPES']
    # Titles = config['Titles']
    # %%
    ts_norm = z
    format = config['Formats'][AbsDiffRate][type]
    # print(format)

    # %%

    ts_norm_countries: pd.DataFrame = ts_norm.loc[ts_norm.country.isin(
        countries)].copy()
    # ts_norm_countries.to_csv(f'ts_norm_countries-{typeCriterion}-n={n}.csv',
    #                          index=False)
    fig = None

    if AbsDiffRate in ['Absolute', 'Difference', 'Change(%)']:

        # _, TNORM, TNORM_in_projection = get_TNORM_plus(ts_norm_countries,
        #                                                timehorizon=timehorizon)

        # print(TNORM_in_projection.set_index(['country']).loc['Germany'])
        TNORM = ts_norm_countries

        fig = plot_cases_plus(TNORM, type, TYPES[type], AbsDiffRate)
        # st.plotly_chart(fig)

    fig.update_layout(legend={'title': {'text': 'Country: Day zero'}})
    # st.write(fig.layout)

    fig.update_layout(yaxis={'tickformat': format})
    fig.update_layout(title=type)
    fig.update_layout(xaxis=dict(
        title_text=
        f"Days before/after ... <br>Number of {typeCriterion} cases hit {n}"))

    fig.update_layout(
        title_text=f'<b>{TYPES[type]}</b>',
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

    return fig