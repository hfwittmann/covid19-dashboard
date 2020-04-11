# %%
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_integer_dtype

import numpy as np
import plotly
import plotly.express as px


def getime_n(group, n=100, column='cases', time_column='t'):
    '''
    get time in group which best match cases = n
    '''
    group_out = group.copy()

    index = group.index[(group[column] - n).abs().argmin()]

    group_out.loc[:,
                  'T_norm'] = group[time_column] - group.at[index, time_column]
    group_out.loc[:, 'T_0'] = group.at[index, time_column]

    return group_out


def get_ts_norm(config, ts, n=500):

    # %%
    T_Norm = list()
    ts = ts.copy()
    ts.date = pd.to_datetime(ts.date)
    for type, group in ts.groupby(['country']):
        group_out = getime_n(group, n=n, column='cases', time_column='date')
        T_Norm.append(group_out)

    ts_norm = pd.concat(T_Norm)

    # %%
    ts_norm.loc[:, 'country_T_0'] = ts_norm['country'] + ':' + ts_norm[
        'T_0'].apply(lambda x: x.strftime(config['DateFormatShort']))
    # %%
    ts_norm.loc[:, 'T_norm_days'] = ts_norm.T_norm.dt.days

    return ts_norm


# %%
# t = np.arange(100)
# A = 1 + np.arange(100)
# B = 13 + np.arange(100)
# C = 17 + np.arange(100)

# # %%
# # D = pd.DataFrame({'t': t, 'A': A, 'B': B, 'C': C})

# # %%
# D_A = D = pd.DataFrame({'t': t, 'country': 'A', 'cases': A})
# D_B = D = pd.DataFrame({'t': t, 'country': 'B', 'cases': B})
# D_C = D = pd.DataFrame({'t': t, 'country': 'C', 'cases': C})
# D = pd.concat([D_A, D_B, D_C])
# D

# # %%

# D_norm = D.groupby([
#     'country'
# ]).apply(lambda x: getime_n(x, n=99, column='cases', time_column='t'))

# D_norm.loc[D_norm['T_norm'] > 0]

# D_norm

# # t	country	cases	T_norm	T_0
# # 0	0	A	1	-98	98
# # 1	1	A	2	-97	98
# # 2	2	A	3	-96	98
# # 3	3	A	4	-95	98
# # 4	4	A	5	-94	98
# # ...	...	...	...	...	...
# # 95	95	C	112	13	82
# # 96	96	C	113	14	82
# # 97	97	C	114	15	82
# # 98	98	C	115	16	82
# # 99	99	C	116	17	82
# # 300 rows × 5 columns

# %%
