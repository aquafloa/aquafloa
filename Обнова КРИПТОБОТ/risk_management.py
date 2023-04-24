import math

class RiskManagement:
    def __init__(self, trading_params):
        self.trading_params = trading_params

    def calculate_position_size(self, stop_loss_percent):
        ticker_data = self.trading_params.ticker_data
        account_balance = self.trading_params.available_balance
        risk_percent = self.trading_params.risk_percent
        margin = self.trading_params.margin
        max_open_trades = self.trading_params.max_open_trades
        max_trades_per_pair = self.trading_params.max_trades_per_pair

        stop_loss_distance = abs(ticker_data['price'] - ticker_data['price'] * stop_loss_percent)
        pip_value = self.trading_params.lot_size / stop_loss_distance
        risk_amount = account_balance * (risk_percent / 100)
        max_loss_amount = risk_amount / max_open_trades
        position_size = math.floor(max_loss_amount / pip_value)

        if position_size > margin:
            position_size = margin

        if position_size > margin / max_trades_per_pair:
            position_size = margin / max_trades_per_pair

        return position_size

    def get_stop_loss_percent(self, current_price, entry_price, account_balance, risk_percent):
        stop_loss_distance = current_price - entry_price
        pip_value = self.trading_params.lot_size / stop_loss_distance
        max_loss_amount = account_balance * (risk_percent / 100)
        stop_loss_percent = max_loss_amount / (pip_value * entry_price)
        return stop_loss_percent

    def calculate_order_size(self, entry_price, account_balance, stop_loss_percent=None, current_price=None, max_open_trades=None, max_trades_per_pair=None, lot_size=None):
        if stop_loss_percent is None:
            stop_loss_percent = self.trading_params.stop_loss_percent
        else:
            risk_percent = self.trading_params.risk_percent
            balance = self.trading_params.available_balance
            stop_loss_percent = self.get_stop_loss_percent(current_price, entry_price, balance, risk_percent)

        if current_price is None:
            current_price = self.trading_params.ticker_data['price']

        if max_open_trades is None:
            max_open_trades = self.trading_params.max_open_trades

        if max_trades_per_pair is None:
            max_trades_per_pair = self.trading_params.max_trades_per_pair

        if lot_size is None:
            lot_size = self.trading_params.lot_size

        ticker_data = self.trading_params.ticker_data
        margin = self.trading_params.margin

        stop_loss_distance = abs(entry_price - entry_price * stop_loss_percent)
        pip_value = lot_size / stop_loss_distance
        risk_amount = account_balance * (self.trading_params.risk_percent / 100)
        max_loss_amount = risk_amount / max_open_trades
        order_size = math.floor(max_loss_amount / pip_value)

        if order_size > margin:
            order_size = margin

        if order_size > self.calculate_position_size(stop_loss_percent) / max_trades_per_pair:
            order_size = self.calculate_position_size(stop_loss_percent) / max_trades_per_pair

        return order_size

    def calculate_take_profit(self,entry_price, take_profit_percent):
        """
        Calculate the take profit price based on the entry price and take profit percentage.
        """
        take_profit_price = entry_price + entry_price * take_profit_percent
        return take_profit_price
