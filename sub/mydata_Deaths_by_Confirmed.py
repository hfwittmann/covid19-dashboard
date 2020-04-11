# %%
import numpy as np
import streamlit as st

import pandas as pd


def mydata_Deaths_by_Confirmed(D_D,
                               D_C,
                               index_cols=['Date'],
                               value_cols=['Value'],
                               type='Death_Rate'):
    '''
    # 	type	Value
    # Date
    # 1	Confirmed	11
    # 1	Deaths	12
    # 2	Confirmed	13
    # 2	Deaths	14
    # 3	Confirmed	15
    # 3	Deaths	16

    is turned into

    # 	type	Value
    # Date
    # 1	Death_Rate	1.090909
    # 2	Death_Rate	1.076923
    # 3	Death_Rate	1.066667

    '''

    assert type in ['C_by_D', 'Death_Rate']

    D_D = D_D.set_index(index_cols)[value_cols]
    D_C = D_C.set_index(index_cols)[value_cols]

    Rates = {
        'Death_Rate': lambda: D_D / D_C  # percent
    }

    D_R = Rates[type]()
    D_R['type'] = type

    return D_R.reset_index()

