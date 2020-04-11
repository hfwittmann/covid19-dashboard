import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# def plotMap(z = df['GDP (BILLIONS)'], locations=df['CODE'], text = df['country']):
def plotMap(z, type, AbsDiffRate, LogScale, datecode, color_continuous_scale,
            reverse_color, config):

    ccs = color_continuous_scale

    if reverse_color:
        ccs = ccs + '_r'

    colorrange = config['Override_ColorRanges'][AbsDiffRate][type]

    if colorrange != {}:
        colorrange['range_color'] = tuple(colorrange['range_color'])

    fig = px.choropleth(
        z,
        locations='CODE',
        scope="world",
        color=AbsDiffRate,
        color_continuous_scale=ccs,  # [(0, "blue"), (1, "red")],  # 'Reds'
        hover_name='country',
        labels={AbsDiffRate: ''},  #ColorBar[AbsDiffRate]},
        **colorrange)

    # print(fig.data[0].hovertemplate)
    # remove part of hovertemplate
    fig.data[0].hovertemplate = fig.data[0].hovertemplate.replace(
        "<br>CODE=%{location}", "")

    format = config['Formats'][AbsDiffRate][type]

    fig.data[0].hovertemplate = fig.data[0].hovertemplate.replace(
        "%{z}", f"%{{z:{format}}}")
    fig.update_layout(coloraxis_colorbar=dict(tickformat=format))

    fig.for_each_trace(lambda trace: trace.update(marker_line=dict(
        color='darkgray', width=0.5)))

    fig.update_layout(coloraxis_colorbar=dict(
        title=config['ColorBar'][AbsDiffRate][type]))

    Colors = fig.layout['coloraxis']['colorscale']

    Spaces = {
        'Absolute': lambda: np.logspace(-5, 0, len(Colors)),
        'Difference': lambda: np.logspace(-5, 0, len(Colors)),
        'Change(%)': lambda: np.linspace(0, 1, len(Colors))
    }

    Space = Spaces[AbsDiffRate]()
    Space[0] = 0.0

    newColorscale = [(float(l), c[1]) for (l, c) in zip(Space, Colors)]
    fig.update_layout(coloraxis_colorscale=newColorscale)
    # fig.layout['coloraxis']['colorscale'] = newColorscale

    TYPES = config['TYPES']
    Titles = config['Titles']

    fig.update_layout(
        title_text=f'<b>{TYPES[type]}</b>',
        geo=dict(showframe=False,
                 showcoastlines=False,
                 projection_type='equirectangular'),
        annotations=[
            dict(
                x=0.55,
                y=0.1,
                xref='paper',
                yref='paper',
                text=
                'Source: <a href="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series">\
                Johns Hopkins CSSE</a>',
                showarrow=False)
        ])
    return fig
