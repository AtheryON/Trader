import time
from logger import Logger

class LiveTrader:
    def __init__(self, strategy, order_manager, risk_manager, trading_pairs, timeframe, limit, take_profit_percentage):
        self.strategy = strategy
        self.order_manager = order_manager
        self.risk_manager = risk_manager
        self.trading_pairs = trading_pairs
        self.timeframe = timeframe
        self.limit = limit
        self.take_profit_percentage = take_profit_percentage
        # Create instance of Logger with reference to log widget
        self.logger = Logger(__name__)

    def run(self):
        try:
            while True:
                for symbol in self.trading_pairs:
                    # Get the current price data for the symbol.
                    candles = self.order_manager.binance.fetch_candles(symbol, self.timeframe, self.limit)

                    # Update the strategy with the current symbol's candles.
                    self.strategy.candles = candles
                    signal = self.strategy.run()

                    # Check if we should place an order.
                    if signal.iloc[-1] == 'buy':
                        self.order_manager.logger.info(f"{symbol}: Placing market buy order...")
                        # Calculate the position size based on the current price and account balance.
                        price = candles['close'].iloc[-1]
                        position_size = self.risk_manager.get_position_size(symbol, price)
                        self.order_manager.logger.info(f"{symbol}: Position size: {position_size}")

                        # Place the market buy order.
                        order_id = self.order_manager.create_market_order(symbol, 'buy', position_size)

                        # Check if a take profit or stop loss order should be placed.
                        stop_loss_take_profit = self.risk_manager.check_stop_loss_take_profit(symbol, price)
                        if stop_loss_take_profit:
                            # Place the limit take profit order.
                            if stop_loss_take_profit == 'sell':
                                self.order_manager.logger.info(f"{symbol}: Placing limit take profit order...")
                                side = 'sell'
                                amount = position_size
                                price = price + (price * self.risk_manager.take_profit_percentage)
                                self.order_manager.create_limit_order(symbol, side, amount, price)

                            # Place the stop loss order.
                            elif stop_loss_take_profit == 'cancel':
                                self.order_manager.logger.info(f"{symbol}: Placing stop loss order...")
                                self.order_manager.cancel_order(symbol, order_id)

                    elif signal.iloc[-1] == 'sell':
                        self.order_manager.logger.info(f"{symbol}: Placing market sell order...")
                        # Get the position for the symbol.
                        position = self.order_manager.pm.get_position(symbol)

                        # Place the market sell order.
                        order_id = self.order_manager.create_market_order(symbol, 'sell', position['balance'])

                    elif signal.iloc[-1] == 'hold':
                        self.order_manager.logger.info(f"{symbol}: Holding position")
                time.sleep(60)
        except Exception as e:
            self.logger.error(f"An error occurred while running LiveTrader: {e}")
