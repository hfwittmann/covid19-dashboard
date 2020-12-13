# %%
import streamlit as st
from sub.myplot import plotMap


def covid19_maps(config, S):

    st.markdown("""
    # COVID 19 Map Visualization""")

    ######################################### Controls ##############################################
    LogScale = True  # st.sidebar.selectbox('Select Log Scale', options=[True, False])

    st.markdown(f""" ... as of {S['Datecode']}
    """)

    # color_continuous_scale = st.sidebar.selectbox(
    #     'Select Color Scale:', options=px.colors.typed_colorscales())
    Color_continous_scale = config['Color_continous_scale']

    # reverse_color = st.sidebar.selectbox('Reverse color scale:', [False, True])
    Reverse_colors = config['Reverse_colors']

    ######################################### Plotting ##############################################
    for type in S['ConfirmedDeaths']:

        st.write(type)

        D = S.session_state.D[type]
        AbsDiffRate = S['AbsDiffRate'][0]
        Datecode = S['Datecode']

        color_continuous_scale = Color_continous_scale[AbsDiffRate][type]
        reverse_color = Reverse_colors[AbsDiffRate][type]

        D_selection = D.loc[D.date == Datecode]

        # print(D_selection.loc[D_selection.country == 'Germany'])

        fig = plotMap(z=D_selection,
                      type=type,
                      AbsDiffRate=AbsDiffRate,
                      LogScale=LogScale,
                      datecode=Datecode,
                      color_continuous_scale=color_continuous_scale,
                      reverse_color=color_continuous_scale,
                      config=config)

        st.plotly_chart(fig, use_container_width=True)

    return None