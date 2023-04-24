import talib
import numpy as np

class TradingParams:
    def __init__(self, margin, lot_size, pip_size, ticker_data, min_profit, leverage, available_balance, risk_percent, stop_loss_percent, take_profit_percent, max_open_trades, max_trades_per_pair):
        self.margin = margin
        self.ticker_data = ticker_data
        self.lot_size = lot_size
        self.pip_size = pip_size
        self.min_profit = min_profit
        self.leverage = leverage
        self.available_balance = available_balance
        self.risk_percent = risk_percent
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.max_open_trades = max_open_trades
        self.max_trades_per_pair = max_trades_per_pair


    def update_ticker_data(self, exchange, symbol):
        ticker = exchange.fetch_ticker(symbol)
        self.ticker_data = ticker



    def set_stop_loss_take_profit(self):
        close_prices = np.array(self.ticker_data['Close'], dtype='float')
        atr = talib.ATR(self.ticker_data['High'], self.ticker_data['Low'], close_prices, timeperiod=14)
        last_close_price = close_prices[-1]
        if not self.stop_loss_percent:
            self.stop_loss_percent = 2 * atr[-1] / last_close_price
        if not self.take_profit_percent:
            self.take_profit_percent = 4 * atr[-1] / last_close_price
