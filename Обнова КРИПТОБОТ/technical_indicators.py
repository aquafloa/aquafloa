import numpy as np
import pandas as pd
import talib as ta
import ccxt

class TechnicalIndicators:
    """
    A class to represent technical indicators for Bybit exchange.
    """

    def __init__(self, symbol, timeframe='5m'):
        """
        Initializes the TechnicalIndicators object.

        Parameters:
        symbol (str): The symbol to get technical indicators for.
        timeframe (str): The timeframe to get technical indicators for (default='5m').
        """
        self.symbol = symbol
        self.timeframe = timeframe

    def get_historical_data(self, limit=200):
        """
        Gets historical price data for the specified symbol and timeframe.

        Parameters:
        limit (int): The number of candles to retrieve (default=200).

        Returns:
        A pandas dataframe containing the historical price data.
        """
        exchange = ccxt.bybit()
        ohlcvs = exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        headers = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(ohlcvs, columns=headers)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def get_rsi(self, period=14):
        """
        Calculates the Relative Strength Index (RSI) for the specified symbol and timeframe.

        Parameters:
        period (int): The period to calculate RSI for (default=14).

        Returns:
        A pandas dataframe containing the RSI values.
        """
        df = self.get_historical_data()
        print(df)
        rsi = ta.momentum.RSIIndicator(close=df['close'], window=period).rsi()
        return pd.DataFrame({'rsi': rsi}, index=df.index)

    def get_macd(self):
        """
        Calculates the Moving Average Convergence Divergence (MACD) for the specified symbol and timeframe.

        Returns:
        A pandas dataframe containing the MACD and signal line values.
        """
        df = self.get_historical_data()
        macd = ta.trend.MACD(df['close']).macd()
        signal = ta.trend.MACD(df['close']).macd_signal()
        return pd.DataFrame({'macd': macd, 'signal': signal}, index=df.index)

    def get_bbands(self, period=20, std=2):
        """
        Calculates the Bollinger Bands for the specified symbol and timeframe.

        Parameters:
        period (int): The period to calculate the moving average for (default=20).
        std (int): The number of standard deviations to use for the bands (default=2).

        Returns:
        A pandas dataframe containing the upper, middle, and lower band values.
        """
        df = self.get_historical_data()
        upper = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std).bollinger_hband()
        middle = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std).bollinger_mavg()
        lower = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std).bollinger_lband()
        return pd.DataFrame({'upper': upper, 'middle': middle, 'lower': lower}, index=df.index)
