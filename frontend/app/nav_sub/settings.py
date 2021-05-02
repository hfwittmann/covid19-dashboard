import streamlit as st
import datetime
from nav_sub.helper import get_index

from nav_sub.helper import get_set_date
from nav_sub.helper import get_set_selection
from nav_sub.helper import get_set_multiselection


class Settings:
    def __init__(self, session_state):
        self.__settings = {}
        self.session_state = session_state

    def get_set_date(self, *args, **kwargs):
        name = kwargs.get('name')
        key = kwargs.get('key')

        value = get_set_date(*args, **kwargs)
        self.__settings[name] = value
        self.__settings[key] = value

    def get_set_selection(self, *args, **kwargs):
        name = kwargs.get('name')
        key = kwargs.get('key')

        value = get_set_selection(*args, **kwargs)
        self.__settings[name] = value
        self.__settings[key] = value

    def get_set_multiselection(self, *args, **kwargs):
        name = kwargs.get('name')
        key = kwargs.get('key')

        value = get_set_multiselection(*args, **kwargs)
        self.__settings[name] = value
        self.__settings[key] = value

    def place_widget(self, item):

        node_in = self.session_state.tree[item]

        node = node_in.copy()

        for key in node_in:
            if '$' in node_in[key]:
                try:
                    node[key] = eval(str(node_in[key]['$']))
                except Exception as e:
                    pass

        # leave method is constraint is not met
        if 'constraint' in node and not node['constraint']: return None

        widgets = {
            'st.date_input': st.date_input,
            'st.multiselect': st.multiselect,
            'st.selectbox': st.selectbox,
            'st.radio': st.radio,
            'st.sidebar.date_input': st.sidebar.date_input,
            'st.sidebar.multiselect': st.sidebar.multiselect,
            'st.sidebar.selectbox': st.sidebar.selectbox,
            'st.sidebar.radio': st.sidebar.radio,
        }

        first_query_params = self.session_state.first_query_params

        params = st.experimental_get_query_params()
        if not isinstance(params, dict): params = {}

        name = node['name']
        # print()
        # print()
        # print('node', node)
        default_choice = first_query_params[
            name] if name in first_query_params else node['default']

        # widget allows one selection only
        oneselection_only = any(t in node['type']
                                for t in ['selectbox', 'radio'])
        multiselection_possible = any(t in node['type']
                                      for t in ['multiselect'])
        date_type = any(t in node['type'] for t in ['date'])

        input = dict(widget=widgets[node['type']],
                     session_state=self.session_state,
                     name=node['name'],
                     label=node['label'],
                     key=node['name'])

        if date_type:
            value = default_choice[0]
            if isinstance(value, str):
                value = datetime.datetime.strptime(value, '%Y-%m-%d')

            input = {**input, 'value': value}
            self.get_set_date(**input)

        if oneselection_only:
            default_index = get_index(node['options'], default_choice[0])
            input = {
                **input, 'default_index': default_index,
                'options': node['options']
            }
            self.get_set_selection(**input)

        if multiselection_possible:

            options = node['options']

            if '$' in node['options']:
                try:
                    options = node[key] = eval(str(node_in[key]['$']))
                except Exception as e:
                    print(e)



            input = {
                **input, 'default_choices': default_choice,
                'options': options
            }
            # selection = widgets[node['type']](label=node['label'],
            #                                   options=node['options'],
            #                                   default=default_choice,
            #                                   key=node['path'])
            self.get_set_multiselection(**input)

    def __getitem__(self, item):
        return self.__settings[item]
