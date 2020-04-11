# %%
import streamlit as st
import yaml
import pandas as pd
from sub.mydata_change import load_timeseries_change
from app_streamlit_map import covid19_maps
from app_streamlit_timeseries import covid19_timeseries
# from stumpy import stump

# from streamlit import caching
# caching.clear_cache()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

DD = dict(Confirmed=load_timeseries_change('Confirmed'),
          Deaths=load_timeseries_change('Deaths'),
          Death_Rate=load_timeseries_change('Death_Rate'))

# %%
######################################### Controls ##############################################
max_width_str = f"max-width: 100%;"
padding_top: int = 0
padding_right: int = 1
padding_left: int = 1
padding_bottom: int = 10

st.sidebar.markdown("""
# COVID 19 Visualization

This visualisation presents maps and timeseries of the current corona virus pandemic.
""")

visualisation = st.sidebar.selectbox(label="Select Maps or timeseries",
                                     options=['Maps', 'Timeseries'])

st.sidebar.header("Settings")
if visualisation == 'Maps':
    covid19_maps(config, DD)

if visualisation == 'Timeseries':
    covid19_timeseries(config, DD)