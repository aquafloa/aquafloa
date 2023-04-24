import time
from datetime import datetime, timedelta
import pytz
import pandas as pd
import ccxt
import numpy as np
from scalper import Scalper
from trading_params import TradingParams
from pair_data import PairData
from technical_indicators import TechnicalIndicators
from risk_management import RiskManagement
from bybit import BybitClient
from config import API_KEY, API_SECRET

# Set up the exchange
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

symbol = 'ADA/USDT'
ticker = exchange.fetch_ticker(symbol)['info']

class Scalper:
    def __init__(self, api_key, api_secret, symbol, leverage, interval_minutes):
        self.client = BybitClient(api_key, api_secret)
        self.symbol = symbol
        self.leverage = leverage
        self.interval_minutes = interval_minutes

        self.trading_params = TradingParams(
            ticker_data=ticker,
            margin=100,
            lot_size=0.01,
            pip_size=0.0001,
            min_profit=5,
            leverage=1,
            available_balance=6,
            risk_percent=0.02,
            stop_loss_percent=0.01,
            take_profit_percent=0.03,
            max_open_trades=2,
            max_trades_per_pair=10
        )

        self.pair_data = PairData(self.symbol)
        self.technical_indicators = TechnicalIndicators(self.pair_data)
        self.risk_management = RiskManagement(self.trading_params)
        self.orders = []

    def get_current_timestamp(self):
        return datetime.now(pytz.utc)

    def get_interval_start_time(self, current_time):
        interval_start_time = current_time - timedelta(minutes=self.interval_minutes)
        return interval_start_time.replace(second=0, microsecond=0)

    def wait_for_next_interval(self):
        current_time = self.get_current_timestamp()
        next_interval_start_time = self.get_interval_start_time(current_time) + timedelta(minutes=self.interval_minutes)
        time_to_wait = (next_interval_start_time - current_time).total_seconds()
        print(f"Waiting {time_to_wait} seconds for the next interval")
        time.sleep(time_to_wait)

    def get_candle_data(self):
        current_time = self.get_current_timestamp()
        interval_start_time = self.get_interval_start_time(current_time)

        df = self.client.get_kline_data(self.symbol, self.interval_minutes, interval_start_time)
        df = pd.DataFrame(df, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def place_order(self, order_type, quantity, price, reduce_only=False):
        order = self.client.place_order(self.symbol, order_type, quantity, price, reduce_only)
        if 'error' in order:
            print(f"Error placing order: {order['error']['message']}")
            return None
        else:
            print(f"Successfully placed {order_type} order for {quantity} contracts at {price}")
            self.orders.append(order['result'])
            return order['result']

    def close_position(self, reduce_only=False):
        position = self.client.get_position(self.symbol)
        if position['size'] == 0:
            print("Position already closed")
            return
        order_type = 'Sell' if position['side'] == 'Buy' else 'Buy'
        quantity = abs(position['size'])
        price = self.pair_data.get_price(order_type)
        self.place_order(order_type, quantity, price, reduce_only)

    def cancel_all_orders(self):
        if len(self.orders) == 0:
            print("No orders to cancel")
            return
        for order in self.orders:
            result = self.client.cancel_order(order['order_id'])
            if 'error' in result:
                print(f"Error cancelling order {order['order_id']}: {result['error']['message']}")
        else:
            print(f"Successfully cancelled order {order['order_id']}")
            self.orders = []


    def run(self):
        while True:
            try:
                df = self.get_candle_data()
                if len(df) == 0:
                    self.wait_for_next_interval()
                    continue

                self.trading_params.available_balance = self.client.get_available_balance(self.trading_params.margin_currency)

                if len(self.orders) > 0:
                    for order in self.orders:
                        order_status = self.client.get_order_status(order['order_id'])
                        if order_status['order_status'] == 'Filled':
                            self.orders.remove(order)
                            print(f"Order {order['order_id']} filled")

                if self.risk_management.check_max_open_trades(self.orders):
                    self.wait_for_next_interval()
                    continue

                signal = self.technical_indicators.get_signal(df)

                if signal == 'Buy':
                    if self.risk_management.check_max_trades_per_pair('Buy'):
                        self.wait_for_next_interval()
                        continue
                    self.place_order('Buy', self.trading_params.lot_size, self.pair_data.get_price('Buy'))
                elif signal == 'Sell':
                    if self.risk_management.check_max_trades_per_pair('Sell'):
                        self.wait_for_next_interval()
                        continue
                    self.place_order('Sell', self.trading_params.lot_size, self.pair_data.get_price('Sell'))
                elif signal == 'Close':
                    self.close_position()

                self.wait_for_next_interval()

            except Exception as e:
                print(f"Error: {str(e)}")
                self.wait_for_next_interval()
                continue

if __name__ == '__main__':
    api_key = API_KEY
    api_secret = API_SECRET
    symbol = "ADA/USDT"
    leverage = 1
    interval_minutes = 5

    scalper = Scalper(api_key, api_secret, symbol, leverage, interval_minutes)
    while True:
        try:
            scalper.run()
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            scalper.cancel_all_orders()
            scalper.close_position(reduce_only=True)
            scalper.wait_for_next_interval()
