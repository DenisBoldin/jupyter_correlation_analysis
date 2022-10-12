import pandas as pd


class DataLoader:

    @staticmethod
    def load(und1, und2):
        data_1 = DataLoader._load_und(und1)
        data_2 = DataLoader._load_und(und2)
        df = pd.concat([data_1["Adj Close"], data_2["Adj Close"]], axis=1)
        if und1 == und2:
            df.columns = ["{0}1".format(und1), "{0}2".format(und2)]
        else:
            df.columns = [und1, und2]
        return df.dropna()

    @staticmethod
    def _load_und(und):
        try:
            return pd.read_csv('https://github.com/DenisBoldin/jupyter_correlation_analysis/blob/main/data/{0}.csv'.format(und), index_col=0, parse_dates=True)
        except:
            raise Exception("Failed to load data for {0}".format(und))
            
