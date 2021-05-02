import pandas as pd
import pandas_datareader.data as web

from subs.data_preprocessing_0 import get_countries
from subs.data_preprocessing_0 import load_timeseries
from subs.data_preprocessing_1 import get_T0
from subs.data_preprocessing_1 import get_T


def getCountries():
    try:
        countries = get_countries()
        status = 'success'
    except Exception as e:
        countries = None
        status = 'failure'

    return {
        'countries' : countries.to_json(),
        'status': status
    }

def getTimeseries_T(type:str='Death'):


    try:
        # res_death = getTimeseries('Death')
        # timeseries_death = pd.read_json(res_death['timeseries'])
        timeseries_death = load_timeseries('Death')
        country_T0 = get_T0(timeseries_death)


        # res = getTimeseries(type)
        # timeseries = pd.read_json(res['timeseries'])
        timeseries = load_timeseries(type)

        timeseries_T = get_T(country_T0, timeseries)

        return {
            'timeseries': timeseries_T.to_json(),
            'status': 'success'
        }

    except Exception as e:
        print(e)

        return {
            'timeseries' : None,
            'status': 'failure'
        }




if __name__ == '__main__':
    # out = getTimeseries_T('Death')
    out = getTimeseries_T('Confirmed')
    countries = get_countries()


    print('success')