import pandas as pd
import numpy as np
import requests
import io

# %%
# from https://plot.ly/python/choropleth-maps/#world-choropleth-map

import yaml

with open('config/run.yml', 'r') as f:
    config_run = yaml.safe_load(f)


def myclean(D, column='COUNTRY'):

    # try:
    #     print(D.head())
    #     D = D.loc[:, ~D.columns.str.contains('^Unnamed')]
    # except Exception as e:
    #     print(e)

    D[column]=D[column].apply(lambda x:x.split('[')[0])

    # remove () brackets ie Niue (New Zealand) becomes Niue
    D[column]=D[column].apply(lambda x:x.split('(')[0].strip())

    D[column] = D[column].replace({
        'US':
        'United States',
        'Czechia':
        'Czech Republic',
        'Korea, South': 'South Korea',
        'Korea, North': 'North Korea',
        "Cote d'Ivoire": "Ivory Coast",
        "Burma":"Myanmar",
        "Congo":"Congo (Brazzaville)",
        "DR Congo":"Congo (Kinshasa)",
        "Congo, Republic of the": "Congo (Brazzaville)",
        "Congo, Democratic Republic of the": "Congo (Kinshasa)"
    })

    return None



def get_countries():
    countries = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv'
    )

    myclean(countries,'COUNTRY')
    countries_population = get_countries_population()

    countries = pd.merge(countries, countries_population, on='COUNTRY')

    return countries

def get_countries_population():

    url = url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
    # url = "https://en.wikipedia.org/wiki/DAX"
    tables = pd.read_html(url)

    for constituents in tables:
        if 'Change' in constituents.columns: break

    constituents.rename({'Country/Territory':'COUNTRY'}, axis=1, inplace=True)
    myclean(constituents,'COUNTRY')

    return constituents


def load_timeseries(name):
    '''
    Data from 2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE

    of from cache
    '''

    df_chloropleth = get_countries()
    URLS = {
        'Death': 'time_series_covid19_deaths_global',
        'Confirmed': 'time_series_covid19_confirmed_global'
    }

    if config_run['cycle']['mode'] in ['develop', 'production']:
        base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'
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

        df.rename({'Country/Region':'country'}, axis=1, inplace=True)
        myclean(df,'country')
        # print(sorted(df['Country/Region'].unique()))

        df.index = pd.to_datetime(df.index)
        df.columns = ['country', 'state', 'type', 'cases']

        # Move HK to country level
        df.loc[df.state == 'Hong Kong', 'country'] = 'Hong Kong'
        df.loc[df.state == 'Hong Kong', 'state'] = np.nan

        # Move Greenland to country level
        df.loc[df.state == 'Greenland', 'country'] = 'Greenland'
        df.loc[df.state == 'Greenland', 'state'] = np.nan

        # Aggregate countries
        df = df.groupby(['country', 'date',
                        'type']).sum().reset_index(level=['country', 'type'])

        df = df.reset_index().merge(df_chloropleth[['COUNTRY', 'CODE']],
                                    left_on='country',
                                    right_on='COUNTRY')

        df: pd.DataFrame = df.drop(columns=['COUNTRY'], axis=1)

    if config_run['cycle']['mode'] in ['test_fast']:
        df = pd.read_csv(f'data/{name}.csv', index_col=0).head(1000000)


    return df


if __name__ == '__main__':
    print(get_countries().head())
    print(get_countries_population().head())
    print(load_timeseries('Death').head())