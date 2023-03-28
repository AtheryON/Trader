class Config:
    # Binance API parameters
    API_KEY = 'key'
    API_SECRET = 'secret'
    TRADING_PAIRS = ['GALAUSDT', 'OCEANUSDT', 'DOGEUSDT']
    TIMEFRAME = '5m'
    LIMIT = 200

    # Trading strategy parameters
    EMA_FAST = 12
    EMA_SLOW = 26
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    # Trading fee rate
    FEE_RATE = 0.025  # 2.5%

    # Risk management parameters
    STOP_LOSS_PERCENTAGE = 0.05  # 3%
    TAKE_PROFIT_PERCENTAGE = 0.09  # 8%
    RISK_FACTOR_PERCENTAGE = 0.15  # 15%