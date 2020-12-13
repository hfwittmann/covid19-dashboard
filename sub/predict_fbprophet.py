# %%
import streamlit as st
import numpy as np
import pandas as pd
# import stumpy
from sklearn.preprocessing import StandardScaler
# from fbprophet import Prophet

# %%


class Predict():
    def __init__(self, timeseries, periods):
        '''
        timeseries is expected to be a pandas dataframe with a
        - datetime index
        - one column containing the series

        periods is the maximum number of periods the forecast is into the future
        '''
        self.timeseries: pd.DataFrame = timeseries
        self.length = len(self.timeseries)
        self.periods = periods

        self.df = timeseries.dropna()

        self.do_predictions()
        pass

    def __predict(self):
        '''
        timeseries: is a one dimensional timeseries
        index:  the n-th element is the closest match at position n
        '''
        m = Prophet(seasonality_mode='additive',
                    daily_seasonality=False,
                    yearly_seasonality=False,
                    growth='linear')
        m.fit(self.df)

        future = m.make_future_dataframe(periods=self.periods)[-90:]
        forecast = m.predict(future)

        return forecast
        # the predictions are from (window + 1) to (length + 1)

    def do_predictions(self):

        self.forecast = self.__predict()

        pass


# %%
