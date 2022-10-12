import pandas as pd
import numpy as np


class CorrCalculator:
    def __init__(self, data):
        self.data_ = data
        self.tickers_ = data.columns

        self.pair_label_ = ""
        self.corr_label_ = ""
        self.corr_label_method_ = ""
        self.corr_label_final_ = ""
        self.result_ = 0.0

    def calc_corr(self, ret_window, corr_window, smoothing_window, smoothing_method, is_max=True):
        ret = self.__log_returns(self.data_, ret_window)

        self.pair_label_ = "_".join(self.tickers_)
        self.corr_label_ = "{0} {1}D {2}D CORR".format(self.pair_label_, ret_window, corr_window)
        self.corr_label_method_ = "{0} {1} {2}D".format(self.corr_label_, smoothing_method, smoothing_window)
        self.corr_label_final_ = "{0} FINAL CORR".format(self.pair_label_)

        corr = pd.DataFrame()
        corr[self.corr_label_] = self.__rolling_corr(ret, corr_window)

        smoothing_method = smoothing_method.upper()
        if smoothing_method[-1] == "Q":
            quantile = self.__extract_quantile(smoothing_method)
            corr[self.corr_label_method_] = corr.rolling(smoothing_window).quantile(quantile)
        elif smoothing_method == "SMA":
            corr[self.corr_label_method_] = corr.rolling(smoothing_window).mean()
        elif smoothing_method == "EWMA":
            corr[self.corr_label_method_] = corr.ewm(span=smoothing_window, adjust=False).mean()
        else:
            raise Exception("Smoothing method not known")

        corr.dropna(inplace=True)

        if is_max:
            corr[self.corr_label_final_] = corr[[self.corr_label_, self.corr_label_method_]].max(axis=1)
        else:
            corr[self.corr_label_final_] = corr[self.corr_label_method_]

        self.result_ = corr[self.corr_label_final_].iloc[-1].round(4)

        return corr.drop(columns=[self.corr_label_method_])

    @staticmethod
    def __log_returns(data, days):
        return np.log(data / data.shift(days)).dropna().copy()

    @staticmethod
    def __rolling_corr(ret_data, window):
        cols = ret_data.columns
        return ret_data.rolling(window).corr()[cols[0]].dropna().loc[:, cols[1]]

    @staticmethod
    def __extract_quantile(quantile_string):
        return int(quantile_string.upper().replace("Q", "")) * 0.01
