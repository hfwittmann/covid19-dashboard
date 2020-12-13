import pandas as pd
import numpy as np

# from sub.predict import Predict
from sub.predict_fbprophet import Predict as PredictProphet


class GroupPredict():
    def __init__(self,
                 window,
                 DD,
                 groupby='timeseries',
                 date='T',
                 series='Y',
                 periods=5):
        self.window = window
        self.DD = DD
        self.groupby = groupby
        self.date = date
        self.series = series
        self.periods = periods

        pass

    def __ingroup_prediction(self, name, group: pd.DataFrame):
        # print(name)

        timeseries = group.rename(columns={
            'date': 'ds',
            self.series: 'y'
        }).loc[:, ['ds', 'y']]

        # print(timeseries.columns)

        # P = Predict(timeseries, self.window)
        prophet: pd.DataFrame = PredictProphet(timeseries=timeseries,
                                               periods=self.periods)

        forecast = prophet.forecast

        forecast.rename(columns={'yhat': 'prediction'}, inplace=True)
        forecast.rename(columns={'yhat_upper': 'upper_bound'}, inplace=True)
        forecast.rename(columns={'yhat_lower': 'lower_bound'}, inplace=True)

        group = group.merge(forecast,
                            left_on='date',
                            right_on='ds',
                            how='outer')

        group['delta_upper_bound'] = group['upper_bound'] - group['prediction']
        group['delta_lower_bound'] = group['prediction'] - group['lower_bound']

        group['delta_upper_bound'] = np.nan_to_num(group['delta_upper_bound'])
        group['delta_lower_bound'] = np.nan_to_num(group['delta_lower_bound'])

        group['baseline'] = group[self.series].shift(1)
        group['prediction_error'] = group[self.series] - group['prediction']
        group['baseline_error'] = group[self.series] - group['baseline']

        group[self.groupby] = name

        return group

    def do(self):

        self.DD_prediction = list()

        for name, group in self.DD.groupby([self.groupby]):
            group = self.__ingroup_prediction(name, group)
            self.DD_prediction.append(group)

        self.DD = pd.concat(self.DD_prediction)
        # self.DD.set_index([self.date], inplace=True)

        pass