# %%
import streamlit as st
import yaml
from sympy.parsing.sympy_parser import parse_expr

from sub.data import Data

from app_maps import covid19_maps
from app_timeseries import covid19_timeseries

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

from nav_sub import SessionState
from nav_sub.settings import Settings

with open('navigation_covid19.yaml', 'r') as f:
    tree = yaml.safe_load(f)

query_params = st.experimental_get_query_params()

D = Data()
options_date_map = sorted(D['Confirmed'].date.dt.strftime(
    config['DateFormatList']).unique(),
                          reverse=True)

session_state = SessionState.get(first_query_params=query_params,
                                 tree=tree,
                                 D=D,
                                 options_date_map=options_date_map)

S = Settings(session_state)

##################################################################################################################################
from nav_sub.github_icon import github_forkme
st.markdown(github_forkme, unsafe_allow_html=True)
##################################################################################################################################

st.sidebar.markdown("""
# COVID 19 Visualization
This visualisation presents maps and timeseries of the current corona virus pandemic.
""")

S.place_widget('Visualisation')
S.place_widget('ConfirmedDeaths')
S.place_widget('AbsDiffRate')

S.place_widget('Countries')
if S['Visualisation'] in ['Timeseries']:
    st.sidebar.header("Define day zero")
S.place_widget('Day_Zero')
S.place_widget('Date')

if S['AbsDiffRate'] == 'Change(%)':
    st.sidebar.markdown(
        '*Remark: The Change(%) is averaged over the previous 3 days*')

# %%
if S['Visualisation'] == 'Maps':
    covid19_maps(config, S)

if S['Visualisation'] == 'Timeseries':
    covid19_timeseries(config, S)