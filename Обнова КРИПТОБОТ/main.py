import ccxt
import time
from datetime import datetime
from strategy import execute_strategy, run_strategy
from trading_params import TradingParams
from strategy import run_strategy
from config import API_KEY, API_SECRET

# Set up the exchange
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

symbol = 'ADA/USDT'
ticker = exchange.fetch_ticker(symbol)

def main():
    print("Scalping strategy is running...")

    # Set trading parameters
    trading_params = TradingParams(
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


    # Set up the exchange
    exchange.load_markets()
    balance = exchange.fetch_balance()
    usdt_balance = balance['USDT']['total']
    print("USDT Balance:", usdt_balance)
    exchange_symbol = exchange.market(symbol)
    print(exchange_symbol['info'])
    usdt_balance = exchange.fetch_balance()['USDT']['total']
    trading_params.pip_size = exchange_symbol['precision']['price']
    trading_params.min_profit = exchange_symbol['limits']['amount']['min']

    # Check for 'leverage' key in exchange symbol
    if 'leverage' in exchange_symbol:
        trading_params.leverage = 1
        print("Leverage:", trading_params.leverage)
    else:
        print("Warning: 'leverage' key not found in exchange symbol")
        trading_params.leverage = None


    # Run the strategy
    run_strategy(trading_params, exchange, symbol)


if __name__ == '__main__':
    main()
