from sub.mydata_change import load_timeseries_change


class Data:
    def __init__(self):
        self.__get_data__()

    def __get_data__(self):
        self.DD = dict()
        self.DD['Confirmed'] = load_timeseries_change('Confirmed')
        self.DD['Deaths'] = load_timeseries_change('Deaths')
        self.DD['Death_Rate'] = load_timeseries_change('Death_Rate')

    def __getitem__(self, item):
        return self.DD[item]

    def __setitem__(self, item, value):
        self.DD[item] = value
