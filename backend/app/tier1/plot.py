import d6tflow
from tasks.getPlots import Task_getPlot

def wrap_getPlot(type='Death', plottype='timeseries'):
    from datetime import date

    runDate = date.today()
    d6tflow.run(
        Task_getPlot(
            runDate=runDate,
            plottype='timeseries',
            type='Death'
        )
    )

    outSuccess = Task_getPlot(
            runDate=runDate,
            plottype='timeseries',
            type='Death'
        ).output().load()

    return outSuccess



if __name__ == '__main__':

    outSuccess = wrap_getPlot(type='Death', plottype='timeseries')

    print()
    print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(outSuccess['status'])

    print()
    print(outSuccess)

