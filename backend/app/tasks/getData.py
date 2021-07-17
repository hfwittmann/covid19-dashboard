import d6tflow
from d6tflow.tasks import TaskJson
import pandas as pd

from subs.getData import getCountries
from subs.getData import getTimeseries_T



class Task_getCountries(TaskJson):
    runDate = d6tflow.DateParameter()
    def run(self):
        out = getCountries()
        self.save(out)

class Task_getData(TaskJson):

    runDate = d6tflow.DateParameter()
    type = d6tflow.Parameter()

    def run(self):

        timeseries = getTimeseries_T(self.type)
        self.save(timeseries)

@d6tflow.requires(Task_getData)
class Task_getDates(TaskJson):

    runDate = d6tflow.DateParameter()
    type = d6tflow.Parameter()

    def run(self):
        input = self.input().load()

        status, timeseries = input['status'], input['timeseries']

        if status == 'failure':
            self.save({'status': status, 'dates': None})
            return None



        timeseries = pd.read_json(timeseries)
        options_date_map = sorted(timeseries['date'].unique(), reverse=True)

        options_date_map = pd.DataFrame({'date':options_date_map})
        options_date_map['date'] = options_date_map['date'].apply(lambda x: x.strftime('%Y-%m-%d'))


        out =  {
            'timeseries': options_date_map.to_json(),
            'status': 'success'
        }

        self.save(out)


if __name__ == '__main__':
    from datetime import date

    runDate = date.today()

    ### produce success
    d6tflow.run(Task_getData(runDate=runDate, type='Confirmed'))
    outSuccess = Task_getData(runDate=runDate,
                                  type='Confirmed').output().load()


    print()
    print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(outSuccess['status'])


    # ### produce success
    # d6tflow.run(Task_getData(runDate=runDate, type='Death'))
    # outSuccess = Task_getData(runDate=runDate,
    #                               type='Death').output().load()


    # print()
    # print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # print(outSuccess['status'])




    # ##################
    # d6tflow.run(Task_getCountries(runDate=runDate))
    # outSuccess = Task_getCountries(runDate=runDate).output().load()

    # print()
    # print('Should be successful !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # print(outSuccess['status'])



    # # produce failure
    # d6tflow.run(Task_getData(runDate=runDate, type='Blubber'))
    # outFailure = Task_getData(runDate=runDate,
    #                               type='Blubber').output().load()

    # print()
    # print('Intentional Falure !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # print(outFailure['status'])
