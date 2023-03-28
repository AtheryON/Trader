from logger import Logger

class PortfolioManager:
    def __init__(self, binance, fee_rate):
        self.binance = binance
        self.positions = {}
        self.balance = self.binance.fetch_balance()
        self.fee_rate = fee_rate
        self.logger = Logger(__name__)

    def get_position(self, symbol):
        try:
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'balance': 0.0,
                    'cost': 0.0,
                    'profit': 0.0
                }
            return self.positions[symbol]
        except Exception as e:
            self.logger.error(f"Error getting position for {symbol}: {e}")

    def update_position(self, symbol, side, amount, price):
        try:
            position = self.get_position(symbol)
            balance = position['balance']
            cost = position['cost']

            if side == 'buy':
                fees = amount * price * self.fee_rate
                total_cost = (amount * price) + fees

                new_balance = balance + amount
                new_cost = (cost * balance + total_cost) / new_balance
                position['balance'] = new_balance
                position['cost'] = new_cost
            elif side == 'sell':
                fees = amount * price * self.fee_rate
                total_proceeds = (amount * price) - fees

                profit_loss = (total_proceeds - (cost * amount))

                new_balance = balance - amount
                position['balance'] = new_balance
                position['profit'] += profit_loss
        except Exception as e:
            self.logger.error(f"Error updating position for {symbol}: {e}")

    def get_balance(self):
        try:
            self.balance = self.binance.fetch_balance()
            self.logger.info(f"Getting balance: {self.balance}")
            return self.balance
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
