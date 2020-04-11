# %%
import numpy as np
import streamlit as st

from sub.fancy_cache import fancy_cache
from sub.mydata import load_timeseries

import pandas as pd


@fancy_cache(ttl=86400 / 4, unique_to_session=False, persist=True)
def load_timeseries_change(name):
    '''
    'Absolute', 'Difference', 'Change(%)'
    '''

    time_series = load_timeseries(name).copy()
    time_series = time_series.assign(
        change=time_series.groupby(['country', 'type'])[['cases']].diff())

    # time_series = time_series.assign(pct_change=time_series.groupby(
    #     ['country', 'type'])[['cases']].pct_change())
    # time_series[['pct_change']] = time_series[['pct_change'
    #                                            ]].replace([np.inf, -np.inf],
    #                                                       np.nan)
    for periods in [1, 2, 3, 4, 5]:
        time_series = time_series.assign(pct_change=time_series.groupby(
            ['country', 'type'])[['cases']].pct_change(periods=periods))

        # Average over periods
        time_series[f'Change(%)_{periods}'] = (
            1 + time_series['pct_change'].replace([np.inf, -np.inf],
                                                  np.nan))**(1 / periods) - 1

        time_series.drop(columns=['pct_change'], inplace=True)

    time_series['Absolute'] = time_series['cases']
    time_series['Difference'] = time_series['change']
    time_series['Change(%)'] = time_series['Change(%)_3']

    time_series['date'] = pd.to_datetime(time_series['date'])
    time_series['date'] = time_series.date

    # time_series.to_csv(f'corona-{name}-change.csv', index=False)

    return time_series