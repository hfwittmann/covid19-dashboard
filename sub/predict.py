# %%
import streamlit as st
import numpy as np
from stumpy import stomp
from sklearn.preprocessing import StandardScaler

# %%


class Predict():
    def __init__(self, timeseries, window):
        self.timeseries = np.array(timeseries, dtype=float)
        self.length = len(self.timeseries)
        self.window = window

        self.do_predictions()
        pass

    def __predict(self, index):
        '''
        timeseries: is a one dimensional timeseries
        index:  the n-th element is the closest match at position n
        '''
        prediction = np.zeros(shape=(len(index))) + np.nan
        upper_bound = np.zeros(shape=(len(index))) + np.nan
        lower_bound = np.zeros(shape=(len(index))) + np.nan

        assert len(
            index
        ) == 1 + self.length - self.window, f'lengths should match but are different. {len(index)} vs {1 + self.length - self.window}'

        nomatch = index == -1
        index[nomatch] = 0

        current_positions = range(0, self.length - self.window + 1)
        matched_previous_positions = index

        X_list_current = [
            self.timeseries[position:position + self.window].reshape(-1, 1)
            for position in current_positions
        ]

        X_current = np.concatenate(X_list_current, axis=1)

        X_list_previous = [
            self.timeseries[position:position + self.window + 1].reshape(
                -1, 1)  # or wihtout + 1???
            for position in matched_previous_positions
        ]

        X_previous = np.concatenate(X_list_previous, axis=1)

        Scaler_previous = StandardScaler().fit(
            X=X_previous[:-1])  # or leave out -1 to fit the whole series ??

        # X_previous_transformed = Scaler_previous.transform(X=X_previous)
        X_previous_new_step_transformed = Scaler_previous.transform(
            X=X_previous[-1:])

        Scaler_current = StandardScaler().fit(X=X_current)

        prediction[~nomatch] = Scaler_current.inverse_transform(
            X_previous_new_step_transformed).reshape(-1)[~nomatch]

        upper_bound[~nomatch] = Scaler_current.inverse_transform(
            X_previous_new_step_transformed + 1).reshape(-1)[~nomatch]

        lower_bound[~nomatch] = Scaler_current.inverse_transform(
            X_previous_new_step_transformed - 1).reshape(-1)[~nomatch]

        return prediction, upper_bound, lower_bound
        # the predictions are from (window + 1) to (length + 1)

    def __calc_matches(self):

        self.S = stomp(self.timeseries, m=self.window)

        self.deviation = self.S[:, 0]
        # self.centred_index = np.array(self.S[:, 1], dtype=int)
        self.left_index = np.array(self.S[:, 2], dtype=int)
        # self.right_index = np.array(self.S[:, 3], dtype=int)

        pass

    def do_predictions(self):

        self.__calc_matches()

        # self.centred_match = self.__predict(self.centred_index)
        self.left_match = self.__predict(self.left_index)
        # self.right_match = self.__predict(self.right_index)

        self.prediction, self.upper_bound, self.lower_bound = self.left_match  # alias

        pass


# %%
