from subs.orderdict import orderByValue
import requests
import json
import streamlit as st
import pandas as pd

import requests

from environs import Env
env = Env()
env.read_env()

# @st.cache
def get_countries():


    _ = requests.get(f"http://{env('HOST')}:5000/api/getCountries")

    status = _.json()['status']
    countries = pd.read_json(_.json()['countries'])

    return status, countries

# @st.cache
def get_data(type: str):
    assert type in ['Death', 'Confirmed']


    _ = requests.get(f"http://{env('HOST')}:5000/api/getTimeseries_T/{type}")

    status = _.json()['status']
    timeseries = pd.read_json(_.json()['timeseries'],convert_dates=['T0', 'date'])

    try:
        timeseries['date'] = pd.to_datetime(timeseries['date']).apply(lambda x: x.date())
        timeseries['T0'] = pd.to_datetime(timeseries['T0']).apply(lambda x: x.date())
    except Exception as e:
        print(e)



    return status, timeseries


# @st.cache
# def get_plot(type:str, plottype:str):

#     assert type in ['Death', 'Confirmed']
#     assert plottype in ['timeseries']
#     _ = requests.get(
#         f"http://{env('HOST')}:5000/api/plot/{type}/{plottype}")

#     status = _.json()['status']
#     fig = json.loads(_.json()['plot'])


#     return status, fig

if __name__ == "__main__":
    print(get_plot('Death', 'timeseries'))