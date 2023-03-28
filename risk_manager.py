# risk_manager.py file
import traceback
from logger import Logger

class RiskManager:
    def __init__(self, portfolio_manager, stop_loss_percentage, take_profit_percentage, risk_factor_percentage):
        self.pm = portfolio_manager
        self.stop_loss_percentage = stop_loss_percentage
        self.take_profit_percentage = take_profit_percentage
        self.risk_factor_percentage = risk_factor_percentage
        self.min_notional = 12  # minimum notional value for a trade
        # Create instance of Logger with reference to log widget
        self.logger = Logger(__name__)

    # Calculate the maximum amount of capital to risk for a trade based on the available balance and risk factor.
    def get_max_risk(self, symbol):
        try:
            balance = self.pm.get_balance()
            asset_balance = balance[symbol[:-4]]
            open_orders = self.pm.binance.client.fetch_open_orders(symbol)
            order_value = sum([float(order['cost']) for order in open_orders])
            available_balance = asset_balance - order_value
            max_risk = available_balance * self.risk_factor_percentage
            return max_risk
        except Exception:
            self.logger.error(f"Error in get_max_risk for symbol {symbol}: {traceback.format_exc()}")
            return 0

    # Calculate the position size for a trade based on the maximum amount of capital to risk and the current price.
    def get_position_size(self, symbol, price):
        try:
            max_risk = self.get_max_risk(symbol)
            position_size = max_risk / price
            notional_value = position_size * price

            # Check if position size is below minimum notional value, adjust it if needed
            if notional_value < self.min_notional:
                position_size = self.min_notional / price

            return position_size
        except Exception:
            self.logger.error(f"Error in get_position_size for symbol {symbol}: {traceback.format_exc()}")
            return 0

    # Check if a stop loss or take profit order should be placed for a position.
    def check_stop_loss_take_profit(self, symbol, price):
        try:
            position = self.pm.get_position(symbol)
            cost = position['cost']
            balance = position['balance']
            profit_loss = (price - cost) * balance

            if profit_loss < 0:
                # Check if stop loss threshold has been reached
                if abs(profit_loss) > (self.stop_loss_percentage * cost):
                    return 'sell'

            if profit_loss > 0:
                # Check if take profit threshold has been reached
                if profit_loss > (self.take_profit_percentage * cost):
                    return 'sell'

            return None
        except Exception:
            self.logger.error(f"Error in check_stop_loss_take_profit for symbol {symbol}: {traceback.format_exc()}")
            return None
