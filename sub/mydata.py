import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

from sub.mydata_Deaths_by_Confirmed import mydata_Deaths_by_Confirmed
from sub.fancy_cache import fancy_cache

# %%
# from https://plot.ly/python/choropleth-maps/#world-choropleth-map


@st.cache(allow_output_mutation=True)
def get_countries():
    df_chloropleth = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv'
    )
    return df_chloropleth


@fancy_cache(ttl=86400 / 4, unique_to_session=False, persist=True)
def load_timeseries(
    name,
    base_url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'
):
    '''
    Data from 2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE
    '''

    if name in ['Death_Rate']:
        # date,country,type,cases,COUNTRY,CODE

        D_D, D_C = load_timeseries('Deaths'), load_timeseries('Confirmed')

        df = mydata_Deaths_by_Confirmed(D_D,
                                        D_C,
                                        index_cols=['date', 'country', 'CODE'],
                                        value_cols=['cases'],
                                        type=name)

        return df

    df_chloropleth = get_countries()

    URLS = {
        'Deaths': 'time_series_covid19_deaths_global',
        'Confirmed': 'time_series_covid19_confirmed_global'
    }

    url = f'{base_url}/{URLS[name]}.csv'
    # print(url)
    csv = requests.get(url).text

    df = pd.read_csv(
        io.StringIO(csv),
        index_col=['Country/Region', 'Province/State', 'Lat', 'Long'])

    df['type'] = name.lower()
    df.columns.name = 'date'

    df = (df.set_index('type', append=True).reset_index(
        ['Lat', 'Long'], drop=True).stack().reset_index().set_index('date'))

    # in the John Hopkins Data Set the USA is called US, so we have to do some renaming using replace
    # https://stackoverflow.com/questions/19919891/is-there-a-way-to-do-this-series-map-in-place
    df['Country/Region'] = df['Country/Region'].replace({
        'US':
        'United States',
        'Czechia':
        'Czech Republic'
    })

    # print(sorted(df['Country/Region'].unique()))

    df.index = pd.to_datetime(df.index)
    df.columns = ['country', 'state', 'type', 'cases']

    # Move HK to country level
    df.loc[df.state == 'Hong Kong', 'country'] = 'Hong Kong'
    df.loc[df.state == 'Hong Kong', 'state'] = np.nan

    # Aggregate countries
    df = df.groupby(['country', 'date',
                     'type']).sum().reset_index(level=['country', 'type'])

    df = df.reset_index().merge(df_chloropleth[['COUNTRY', 'CODE']],
                                left_on='country',
                                right_on='COUNTRY')

    df: pd.DataFrame = df.drop(columns=['COUNTRY'], axis=1)

    return df
