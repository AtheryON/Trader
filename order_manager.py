from logger import Logger

class OrderManager:
    def __init__(self, binance, portfolio_manager, risk_manager):
        self.binance = binance
        self.pm = portfolio_manager
        self.rm = risk_manager
        self.logger = Logger(__name__)

    def create_market_order(self, symbol, side, amount):
        try:
            order_id = self.binance.create_market_order(symbol, side, amount)
            self.update_position_after_order(symbol, side, amount)
            self.logger.info(f"Placed market {side} order for {amount} {symbol}")
            return order_id
        except Exception as e:
            self.logger.error(f"Error placing market {side} order for {amount} {symbol}: {str(e)}")
            return None

    def create_limit_order(self, symbol, side, amount, price):
        try:
            order_id = self.binance.create_limit_order(symbol, side, amount, price)
            order_status = self.binance.fetch_order_status(symbol, order_id)
            if order_status == 'closed':
                self.update_position_after_order(symbol, side, amount)
            self.logger.info(f"Placed limit {side} order for {amount} {symbol} at {price}")
            return order_id
        except Exception as e:
            self.logger.error(f"Error placing limit {side} order for {amount} {symbol} at {price}: {str(e)}")
            return None

    def cancel_order(self, symbol, order_id):
        try:
            result = self.binance.cancel_order(symbol, order_id)
            self.update_position_after_order(symbol, 'cancel', 0)
            self.logger.info(f"Cancelled order {order_id} for {symbol}")
            return result
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id} for {symbol}: {str(e)}")
            return None

    def update_position_after_order(self, symbol, side, amount):
        try:
            price = self.binance.client.fetch_ticker(symbol)['last']
            if side == 'buy':
                self.pm.update_position(symbol, 'buy', amount, price)
            elif side == 'sell':
                self.pm.update_position(symbol, 'sell', amount, price)
            elif side == 'cancel':
                position = self.pm.get_position(symbol)
                balance = position['balance']
                self.pm.update_position(symbol, 'sell', balance, price)
        except Exception as e:
            self.logger.error(f"Error updating position for {symbol} after {side} order: {str(e)}")
