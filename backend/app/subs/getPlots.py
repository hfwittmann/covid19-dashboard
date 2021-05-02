import json
import plotly
import plotly.express as px


def timeseries_plot(timeseries_data, y='cases'):

    assert y in ['cases', 'diffs']

    thisplot = px.scatter(timeseries_data,
                          x='T',
                          y=y,
                          color='country',
                          hover_data=['date'],
                          log_y=True)

    fig_performance = dict(data=thisplot.data, layout=thisplot.layout)

    return json.dumps(fig_performance, cls=plotly.utils.PlotlyJSONEncoder)



def getPlot(plottype, timeseries_data, status):

    plots = {
        'timeseries': timeseries_plot
        # 'maps
    }

    return {'status': status, 'plot': plots[plottype](timeseries_data)}
