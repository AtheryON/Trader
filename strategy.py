import talib
from logger import Logger

class Strategy:
    def __init__(self, candles, ema_fast, ema_slow, macd_fast, macd_slow, macd_signal):
        self.candles = candles
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.logger = Logger(__name__)

    def run(self):
        try:
            ema_fast = talib.EMA(self.candles['close'], timeperiod=self.ema_fast)
            ema_slow = talib.EMA(self.candles['close'], timeperiod=self.ema_slow)
            macd, signal, _ = talib.MACD(self.candles['close'], fastperiod=self.macd_fast, slowperiod=self.macd_slow,
                                         signalperiod=self.macd_signal)

            signals = []
            for i in range(len(self.candles)):
                if ema_fast[i] > ema_slow[i] and macd[i] > signal[i]:
                    signals.append('buy')
                elif ema_fast[i] < ema_slow[i] and macd[i] < signal[i]:
                    signals.append('sell')
                else:
                    signals.append('hold')

            self.candles['signal'] = signals
            return self.candles['signal']
        except Exception as e:
            self.logger.error(f"An error occurred while running the strategy: {e}")
            return None

