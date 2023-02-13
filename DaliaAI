import ccxt
import pandas as pd
import numpy as np
import time
import logging
import ta
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handler and formatter to the logger
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TradingBot:
    def __init__(self, api_key, api_secret, symbol, budget, interval='1d'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol
        self.interval = interval
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret
        })
        self.amount = budget
        self.budget = budget
        self.data = None
        self.profit = 0
        self.model = None

    def connect_to_exchange(self):
        try:
            self.exchange.load_markets()
            if 'fetchOHLCV' in self.exchange.has:
                logger.info("Successfully connected to the exchange")
            else:
                logger.error("Failed to connect to the exchange")
        except Exception as e:
            logger.error(f"Error while connecting to the exchange: {e}")
            raise

    def retrieve_data(self):
        try:
            self.data = pd.DataFrame(self.exchange.fetch_ohlcv(self.symbol, self.interval))
            self.data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            self.data.set_index('timestamp', inplace=True)
            logger.info("Successfully retrieved market data")
        except Exception as e:
            logger.error(f"Error while retrieving market data: {e}")
            raise

    def calculate_indicators(self):
        try:
            self.data['ma50'] = self.data['close'].rolling(window=50).mean()
            self.data['ma200'] = self.data['close'].rolling(window=200).mean()
            self.data['bb_upper'] = self.data['close'].rolling(window=20).mean() + 2 * self.data['close'].rolling(window=20).std()
            self.data['bb_lower'] = self.data['close'].rolling(window=20).mean() - 2 * self.data['close'].rolling(window=20).std()
            self.data['rsi'] = ta.momentum.RSIIndicator(self.data['close'].values, window=14).rsi()
            self.data.fillna(0, inplace=True)
            logger.info("Successfully calculated indicators")
        except Exception as e:
            logger.error(f"Error while calculating indicators: {e}")
            raise

    def decide(self):
        try:
            self.data['macd'] = ta.trend.MACD(self.data['close'].values, window_fast=12, window_slow=26, window_sign=9).macd
            self.data['macd_signal'] = ta.trend.MACD(self.data['close'].values, window_fast=12, window_slow=26, window_sign=9).macd_signal
            self.data['momentum'] = ta.momentum.RSIIndicator(self.data['close'].values, window=14).rsi()
            self.data['action'] = np.where((self.data['rsi'] < 30) & (self.data['close'] > self.data['bb_lower']) & (self.data['macd'] > self.data['macd_signal']) & (self.data['momentum'] > 50), 1, 0)
            self.data['action'] = np.where((self.data['rsi'] > 70) & (self.data['close'] < self.data['bb_upper']) & (self.data['macd'] < self.data['macd_signal']) & (self.data['momentum'] < 50), -1, self.data['action'])
            logger.info("Successfully made a decision")
        except Exception as e:
            logger.error(f"Error while making a decision: {e}")
            raise


    def execute_trade(self):
        try:
            if self.data['action'].iloc[-1] == 1:
                self.amount = self.amount / self.data['close'].iloc[-1]
                logger.info(f"Bought {self.amount} at {self.data['close'].iloc[-1]}")
            elif self.data['action'].iloc[-1] == -1:
                self.amount = self.amount * self.data['close'].iloc[-1]
                self.profit = self.amount - self.budget
                logger.info(f"Sold {self.amount} at {self.data['close'].iloc[-1]}")
            logger.info("Successfully executed trade")
        except Exception as e:
            logger.error(f"Error while executing trade: {e}")
            raise

    def train_model(self):
        try:
            X = self.data[['close', 'ma50', 'ma200', 'bb_upper', 'bb_lower', 'rsi']]
            y = self.data['action']
            models = [RandomForestClassifier(), SVC(), LogisticRegression(), GaussianNB()]
            best_model = None
            best_score = 0
            for model in models:
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
            logger.info("Successfully trained the model")
            return best_model
        except Exception as e:
            logger.error(f"Error while training the model: {e}")
            raise

    def incorporate_model(self):
        try:
            self.model = self.train_model()
            self.data['model_action'] = self.model.predict(self.data[['close', 'ma50', 'ma200', 'bb_upper', 'bb_lower', 'rsi']])
            logger.info("Successfully incorporated the model into the decision making process")
        except Exception as e:
            logger.error(f"Error while incorporating the model: {e}")
            raise

    def implement_risk_management(self):
        try:
            self.data['stop_loss'] = self.data['close'] * 0.97
            self.data['take_profit'] = self.data['close'] * 1.03
            for i in range(len(self.data) - 1):
                if self.data.at[i, 'action'] == 1:
                    if self.data.at[i, 'low'] <= self.data.at[i, 'stop_loss']:
                        self.data.at[i, 'action'] = -1
                    elif self.data.at[i, 'high'] >= self.data.at[i, 'take_profit']:
                        self.data.at[i, 'action'] = -1
            logger.info("Successfully implemented risk management")
        except Exception as e:
            logger.error(f"Error while implementing risk management: {e}")
            raise

    def monitor_performance(self):
        try:
            self.profit = self.amount - self.budget
            logger.info(f"Current profit: {self.profit}")
            logger.info("Successfully monitored performance")
        except Exception as e:
            logger.error(f"Error while monitoring performance: {e}")
            raise

    def continuously_test_and_refine(self):
        try:
            self.train_model()
            self.incorporate_model()
            logger.info("Successfully tested and refined the bot")
        except Exception as e:
            logger.error(f"Error while testing and refining the bot: {e}")
            raise

    def run_bot(self):
        while True:
            try:
                self.connect_to_exchange()
                self.retrieve_data()
                self.calculate_indicators()
                self.decide()
                self.execute_trade()
                self.incorporate_model()
                self.implement_risk_management()
                self.monitor_performance()
                self.continuously_test_and_refine()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error while running the bot: {e}")
                raise

if __name__ == '__main__':
    api_key =  'key'
    api_secret = 'secret'
    symbol = 'GALA/BUSD'
    budget = 0

    bot = TradingBot(api_key, api_secret, symbol, budget)
    bot.run_bot()
