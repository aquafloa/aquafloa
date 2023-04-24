import ccxt
import time
from datetime import datetime
import talib
from risk_management import RiskManagement
import numpy as np
from config import API_KEY, API_SECRET

# Set up the exchange
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

symbol = 'ADA/USDT'


def execute_strategy(trading_params, exchange, symbol, instance):
    """
    Execute the scalping strategy based on the current price and account balance.
    """
    account_balance = trading_params.available_balance
    risk_percent = trading_params.risk_percent
    stop_loss_percent = trading_params.stop_loss_percent
    take_profit_percent = trading_params.take_profit_percent

    # Get current ticker information
    ticker = exchange.fetch_ticker(symbol)
    ask_price = ticker['ask']
    bid_price = ticker['bid']
    current_price = ticker['last']
    close_prices = ticker['close']  # add this line to get close prices for RSI calculation

    # Calculate entry price
    if 'spread' in ticker:
        spread = ticker['spread']
        entry_price = current_price - (spread / 2)
    else:
        entry_price = (ask_price + bid_price) / 2

    # Calculate order size, stop loss price, and take profit price
    rm = RiskManagement(trading_params)
    rsi = talib.RSI(np.ravel(close_prices), timeperiod=14)
    instance['indicators']['rsi'] = rsi
    order_size = rm.calculate_order_size(entry_price, trading_params.available_balance, rsi, trading_params.stop_loss_percent)
    stop_loss_price = rm.calculate_stop_loss(entry_price, trading_params.stop_loss_percent)
    take_profit_price = rm.calculate_take_profit(entry_price, trading_params.take_profit_percent)

    # Place order based on current price
    if current_price < entry_price:
        # Place buy order with stop loss and take profit
        buy_order = exchange.create_order(symbol=symbol, type='limit', side='buy', amount=order_size, price=entry_price,
                                           stopLoss=stop_loss_price, takeProfit=take_profit_price)
        # Print the results
        profit_loss = (take_profit_price - entry_price) * order_size if take_profit_price > entry_price else (entry_price - stop_loss_price) * order_size * -1
        print(f'Time: {datetime.now()}')
        print(f'Buy Order Price: {entry_price}')
        print(f'Stop Loss Price: {stop_loss_price}')
        print(f'Profit/Loss: {profit_loss}\n')
        return buy_order
    elif current_price > entry_price:
        # Place sell order with stop loss and take profit
        sell_order = exchange.create_order(symbol=symbol, type='limit', side='sell', amount=order_size, price=entry_price,
                                            stopLoss=stop_loss_price, takeProfit=take_profit_price)
        # Print the results
        profit_loss = (entry_price - take_profit_price) * order_size if take_profit_price < entry_price else (stop_loss_price - entry_price) * order_size * -1
        print(f'Time: {datetime.now()}')
        print(f'Sell Order Price: {entry_price}')
        print(f'Stop Loss Price: {stop_loss_price}')
        print(f'Take Profit Price: {take_profit_price}')
        print(f'Profit/Loss: {profit_loss}\n')
        return sell_order



def run_strategy(trading_params, exchange, symbol):
    instance = {'ticker_data': None} # added
    while True:
        try:
            # Get current price
            ticker_data = exchange.fetch_ticker(symbol)
            current_price = ticker_data['last']

            # Check if leverage is set and update if necessary
            if trading_params.leverage is not None:
                exchange.change_leverage(symbol, trading_params.leverage)
                print(f"Leverage updated to {trading_params.leverage}x")

            execute_strategy(trading_params, exchange, symbol, instance)
        except Exception as e:
            print(f"Error executing strategy for {symbol}: {e}")
            print(f"Current price: {current_price}")
            print(f"Trading parameters: {trading_params.__dict__}")
            print(f"Exchange: {exchange}")

        time.sleep(10)
