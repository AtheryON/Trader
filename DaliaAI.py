import ccxt
import pandas as pd
import numpy as np
import time
import logging
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handler and formatter to the logger
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DaliaAI:
    def __init__(self, api_key, api_secret, symbol, budget, interval='5m'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol
        self.interval = interval
        self.limit = 4500
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
            self.data = pd.DataFrame(self.exchange.fetch_ohlcv(self.symbol, self.interval, self.limit))
            self.data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            self.data.set_index('timestamp', inplace=True)
            logger.info(f"Successfully retrieved market data \n {self.data}")
        except Exception as e:
            logger.error(f"Error while retrieving market data: {e}")
            raise

    def calculate_indicators(self):
        try:
            self.data['ma50'] = talib.SMA(self.data['close'].values, timeperiod=50)
            self.data['ma200'] = talib.SMA(self.data['close'].values, timeperiod=200)
            upper, middle, lower = talib.BBANDS(self.data['close'].values, timeperiod=20)
            self.data['bb_upper'] = upper
            self.data['bb_middle'] = middle
            self.data['bb_lower'] = lower
            self.data['rsi'] = talib.RSI(self.data['close'].values, timeperiod=14)
            macd, macd_signal, macd_hist = talib.MACD(self.data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
            self.data['macd'] = macd
            self.data['macd_signal'] = macd_signal
            self.data['macd_hist'] = macd_hist
            logger.info("Successfully calculated indicators")
        except Exception as e:
            logger.error(f"Error while calculating indicators: {e}")
            raise

    def decide(self):
        try:
            if len(self.data) < 2:
                logger.warning("Not enough data to make a decision")
                return
            self.data['action'] = np.where((self.data['rsi'] < 30) & (self.data['close'] > self.data['bb_lower']) & (self.data['macd'] > self.data['macd_signal']) & (self.data['macd_hist'] > 50), 1, 0)
            self.data['action'] = np.where((self.data['rsi'] > 70) & (self.data['close'] < self.data['bb_upper']) & (self.data['macd'] < self.data['macd_signal']) & (self.data['macd_hist'] < 50), -1, self.data['action'])
            self.data.fillna(0, inplace=True)
            logger.info("Successfully made a decision")
        except Exception as e:
            logger.error(f"Error while making a decision: {e}")
            raise

    def execute_trade(self):
        try:
            if self.data['action'].iloc[-1] == 1:
                self.amount = self.amount / self.data['close'].iloc[-1]
                logger.info(f"Bought {self.amount} at {self.data['close'].iloc[-1]}")
                print(f"Bought {self.amount} at {self.data['close'].iloc[-1]}")
            elif self.data['action'].iloc[-1] == -1:
                self.amount = self.amount * self.data['close'].iloc[-1]
                self.profit = self.amount - self.budget
                logger.info(f"Sold {self.amount} at {self.data['close'].iloc[-1]}")
                print(f"Sold {self.amount} at {self.data['close'].iloc[-1]}")
            logger.info(f"Action taken: {self.data['action'].iloc[-1]}")
            print(f"Action taken: {self.data['action'].iloc[-1]}")
            logger.info("Successfully executed trade")
        except Exception as e:
            logger.error(f"Error while executing trade: {e}")
            raise

    def train_model(self):
        X = self.data[['close', 'ma50', 'ma200', 'bb_upper', 'bb_lower', 'rsi', 'macd', 'macd_signal', 'macd_hist']]
        y = np.where(self.data['action'] == 'Buy', 1, 0)
        y = np.where(self.data['action'] == 'Sell', -1, y)

        models = [
            RandomForestClassifier(),
            LogisticRegression(),
            KNeighborsClassifier(),
            DecisionTreeClassifier(),
            SVC(kernel='linear'),
        ]

        best_score = 0
        best_model = None
        for model in models:
            if len(np.unique(y)) > 1:
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
            else:
                logger.error("Error while training the model: This solver needs samples of at least 2 classes in the data, but the data contains only one class")
                return None
        logger.info("Successfully implemented best model")
        return best_model

    def incorporate_model(self):
        try:
            self.model = self.train_model()
            if self.model is not None:
                self.data['model_action'] = np.where(self.model.predict(self.data[['close', 'ma50', 'ma200', 'bb_upper', 'bb_lower', 'rsi', 'macd', 'macd_signal', 'macd_hist']]) > 0, 1, 0)
                self.data['model_action'] = np.where(self.model.predict(self.data[['close', 'ma50', 'ma200', 'bb_upper', 'bb_lower', 'rsi', 'macd', 'macd_signal', 'macd_hist']]) < 0, -1, self.data['model_action'])
        except Exception as e:
            logger.error(f"Error while incorporating the model: {e}")


    def implement_risk_management(self):
        try:
            self.data['stop_loss'] = self.data['close'] * 0.97
            self.data['take_profit'] = self.data['close'] * 1.03
            for i in range(len(self.data) - 1):
                if self.data.iloc[i]['action'] == 1:
                    if self.data.iloc[i]['low'] <= self.data.iloc[i]['stop_loss']:
                        self.data.at[self.data.index[i], 'action'] = -1
                    elif self.data.iloc[i]['high'] >= self.data.iloc[i]['take_profit']:
                        self.data.at[self.data.index[i], 'action'] = -1
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
    api_key = 'key'
    api_secret = 'secret'
    symbol = 'ETH/USDT'
    budget = 500

    bot = DaliaAI(api_key, api_secret, symbol, budget)
    bot.run_bot()
