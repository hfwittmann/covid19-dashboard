from datetime import date
import d6tflow
from tasks.getData import Task_getCountries
from tasks.getData import Task_getDates
from tasks.getData import Task_getData


def wrap_getCountries():
    runDate = date.today()
    d6tflow.run(tasks=Task_getCountries(runDate=runDate))
    outSuccess = Task_getCountries(runDate=runDate).output().load()
    return outSuccess


def wrap_getData(type='Death'):
    runDate = date.today()
    d6tflow.run(Task_getData(runDate=runDate, type=type))
    outSuccess = Task_getData(runDate=runDate,
                                  type=type).output().load()
    return outSuccess

def wrap_getDates(type='Death'):
    runDate = date.today()
    d6tflow.run(Task_getDates(runDate=runDate, type=type))
    outSuccess = Task_getDates(runDate=runDate, type=type).output().load()
    return outSuccess


if __name__ == '__main__':

    outSuccess = wrap_getCountries()

    print()
    print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(outSuccess['status'])

    outSuccess = wrap_getData(type='Death')

    print()
    print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(outSuccess['status'])

    outSuccess = wrap_getDates()
    print()
    print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(outSuccess['status'])