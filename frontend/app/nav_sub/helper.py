import streamlit as st


# %%
def get_index(mylist, element):

    assert isinstance(mylist, list), 'mylist should be a list'

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


def limit_2_allowed_keys(session_state, params):

    tree = session_state.tree

    all_controls = [tree[key]['name'] for key in tree]
    allowed_keys = set(all_controls).intersection(params.keys())

    params = {key: params[key] for key in allowed_keys}

    return params


def get_set_date(widget, session_state, name, key=None, *args, **kwargs):
    '''
    can use as widget:

    st.date_input
    st.sidebar.radio

    '''
    return get_set(widget, session_state, name, key=None, *args, **kwargs)


def get_set_selection(widget, session_state, name, key=None, *args, **kwargs):
    '''
    can use as widget:

    st.selectbox
    st.sidebar.selectbox
    st.radio
    st.sidebar.radio

    '''

    kwargs['index'] = kwargs['default_index']
    del kwargs['default_index']

    return get_set(widget, session_state, name, key=None, *args, **kwargs)


def get_set_multiselection(widget,
                           session_state,
                           name,
                           key=None,
                           *args,
                           **kwargs):
    '''
    can use as widget:

    st.multiselect
    st.sidebar.multiselect

    '''
    first_query_params = session_state.first_query_params

    kwargs['default_choices'] = first_query_params[
        name] if name in first_query_params else kwargs['default_choices']
    # default_indices = get_indices(options, default_choices)
    kwargs['default'] = kwargs['default_choices']
    del kwargs['default_choices']

    return get_set(widget, session_state, name, key=None, *args, **kwargs)


def get_set(widget, session_state, name, key=None, *args, **kwargs):

    if key == None:
        key = name
        kwargs['key'] = key

    params = st.experimental_get_query_params()
    if not isinstance(params, dict): params = {}

    selection = widget(**kwargs)

    dict_selection = {name: selection}

    params = {**params, **dict_selection}
    params = limit_2_allowed_keys(session_state, params)

    st.experimental_set_query_params(**params)

    return selection
