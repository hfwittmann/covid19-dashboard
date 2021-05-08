# %%
import pandas as pd

from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_integer_dtype

import numpy as np
import yaml

with open('config/run.yml', 'r') as f:
    config = yaml.safe_load(f)


def get_T0(timeseries):
    groupby=config['T0']['groupby']
    n=config['T0']['n']
    column=config['T0']['column']
    time_column=config['T0']['time_column']

    timeseries['cases_diff_n'] = (timeseries[column] - n).abs()
    mins= timeseries.groupby([groupby]).apply(lambda x: x.reset_index().loc[x['cases_diff_n'].argmin()])

    return mins[['date']].rename(columns={'date':'T0'})

    # ts_norm.loc[:, 'country_T_0'] = ts_norm['country'] + ':' + ts_norm[
    #     'T_0'].apply(lambda x: x.strftime(config['DateFormatShort']))

def get_T(country_T0, timeseries):
    timeseries_plusT0 = pd.merge(country_T0, timeseries, on='country')

    # timeseries_plusT0['date'] = pd.to_datetime(timeseries_plusT0['date'])
    # timeseries_plusT0['T0'] = pd.to_datetime(timeseries_plusT0['T0'])
    # timeseries_plusT0['T'] = timeseries_plusT0['date']-timeseries_plusT0['T0']


    # timeseries_plusT0['date'] = timeseries_plusT0['date']
    # timeseries_plusT0['T0'] = timeseries_plusT0['T0']
    # timeseries_plusT0['T'] = timeseries_plusT0['T'].apply(lambda x: x.days)

    # changes every day
    # https://stackoverflow.com/questions/20648346/computing-diffs-within-groups-of-a-dataframe
    timeseries_plusT0['1d'] = timeseries_plusT0.groupby(['country'])['cases'].transform(lambda x: x.diff(periods=1))
    timeseries_plusT0['7d'] = timeseries_plusT0.groupby(['country'])['cases'].transform(lambda x: x.diff(periods=7))/7
    timeseries_plusT0['28d'] = timeseries_plusT0.groupby(['country'])['cases'].transform(lambda x: x.diff(periods=28))/28

    timeseries_plusT0['trend'] = timeseries_plusT0['7d']/timeseries_plusT0['28d']



    return timeseries_plusT0
# %%
