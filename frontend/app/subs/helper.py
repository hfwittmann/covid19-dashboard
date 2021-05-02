import streamlit as st


# %%
def get_index(mylist, element):
    if element == -1: return 0  # element not given in deep link

    try:
        element = int(element)
    except:
        pass

    try:
        out = mylist.index(element)
    except:
        out = 0

    return out


def get_indices(mylist, elements):
    return [get_index(mylist, e) for e in elements]


def get_set_selection(widget,
                      name='visualisation',
                      label='Select Maps or Timeseries',
                      options=['Maps', 'Timeseries'],
                      key=None):
    '''
    can use as widget:

    st.selectbox
    st.sidebar.selectbox
    st.radio
    st.sidebar.radio

    '''

    params = st.experimental_get_query_params()
    if not isinstance(params, dict): params = {}
    # st.write(params)
    default_choice = params[name][0] if name in params else -1
    default_index = get_index(options, default_choice)
    selection = widget(label=label,
                       options=options,
                       index=default_index,
                       key=key)

    dict_selection = {name: selection}

    params = {**params, **dict_selection}

    st.experimental_set_query_params(**params)
    # st.write(params)
    return selection


def get_set_multiselection(widget,
                           name='ConfirmedDeath',
                           label='Select Type',
                           options=['Death_Rate', 'Confirmed', 'Death'],
                           default_choices=['Death_Rate', 'Confirmed'],
                           key=None):
    '''
    can use as widget:

    st.multiselect
    st.sidebar.multiselect

    '''

    params = st.experimental_get_query_params()
    if not isinstance(params, dict): params = {}
    # st.write(params)
    default_choices = params[name] if name in params else default_choices
    # default_indices = get_indices(options, default_choices)
    selections = widget(label=label,
                        options=options,
                        default=default_choices,
                        key=key)

    dict_selections = {name: selections}
    params = {**params, **dict_selections}

    st.experimental_set_query_params(**params)
    # st.write(params)
    return selections
