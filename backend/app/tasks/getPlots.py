import d6tflow
from d6tflow.tasks import TaskJson
import pandas as pd

from tasks.getData import Task_getData
from subs.getPlots import getPlot

@d6tflow.requires(Task_getData)
class Task_getPlot(TaskJson):
    runDate = d6tflow.DateParameter()
    plottype = d6tflow.Parameter()

    def run(self):

        Data = self.input().load()

        timeseries_T = pd.read_json(Data['timeseries'])
        status = Data['status']


        if status == 'failure':
            self.save({'status': status, 'plot': None})
            return None

        myplot = getPlot(
            plottype = self.plottype,
            timeseries_data = timeseries_T,
            status = status
        )

        self.save(myplot)


if __name__ == '__main__':
    from datetime import date

    runDate = date.today()

    d6tflow.run(
        Task_getPlot(
            runDate=runDate,
            plottype='timeseries',
            type='Death'
        )
    )

    print(Task_getPlot(
            runDate=runDate,
            plottype='timeseries',
            type='Death'
        ).output().load()['status'])



