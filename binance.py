import ccxt
import pandas as pd
from logger import Logger

class Binance:
    def __init__(self, api_key, api_secret):
        self.client = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        self.logger = Logger(__name__)

    def fetch_balance(self):
        try:
            balance = self.client.fetch_balance()
            return balance['total']
        except Exception as e:
            self.logger.error(f"Error fetching balance: {str(e)}")
            return None

    def fetch_candles(self, symbol, timeframe, limit):
        try:
            candles = self.client.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.drop_duplicates(subset='timestamp')
            df = df.set_index('timestamp')
            return df
        except Exception as e:
            self.logger.error(f"Error fetching candles: {str(e)}")
            return None

    def create_market_order(self, symbol, side, amount):
        try:
            order = self.client.create_market_order(symbol=symbol, side=side, amount=amount)
            return order['id']
        except Exception as e:
            self.logger.error(f"Error creating market order: {str(e)}")
            return None

    def create_limit_order(self, symbol, side, amount, price):
        try:
            order = self.client.create_limit_order(symbol=symbol, side=side, amount=amount, price=price)
            return order['id']
        except Exception as e:
            self.logger.error(f"Error creating limit order: {str(e)}")
            return None

    def cancel_order(self, symbol, order_id):
        try:
            result = self.client.cancel_order(symbol=symbol, id=order_id)
            return result
        except Exception as e:
            self.logger.error(f"Error cancelling order: {str(e)}")
            return None

    def fetch_order_status(self, symbol, order_id):
        try:
            order = self.client.fetch_order(symbol=symbol, id=order_id)
            status = order['status']
            return status
        except Exception as e:
            self.logger.error(f"Error fetching order status: {str(e)}")
            return 'unknown'