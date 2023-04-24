import pandas as pd

class PairData:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.data = None

    def update_data(self, new_data):
        if self.data is None:
            self.data = pd.DataFrame(new_data)
        else:
            self.data = self.data.append(pd.DataFrame(new_data))
        self.data.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
        self.data.set_index('timestamp', inplace=True)

    def get_last_candle(self):
        if self.data is None:
            return None
        else:
            return self.data.iloc[-1]

    def get_candles(self, num_candles):
        if self.data is None:
            return None
        else:
            return self.data.iloc[-num_candles:]
