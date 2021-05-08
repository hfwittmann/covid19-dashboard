from tier1.data import wrap_getCountries
from tier1.data import wrap_getData
from tier1.data import wrap_getDates

def get_todays_data():

    try:
        _ = wrap_getCountries()
        _ = wrap_getData()
        _ = wrap_getDates()

        return 'get_todays_data_succeded'

    except Exception as e:

        return 'get_todays_data_failed'


if __name__ == "__main__":
    get_todays_data()