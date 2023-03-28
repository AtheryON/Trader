from config import Config
from binance import Binance
from strategy import Strategy
from portfolio_manager import PortfolioManager
from risk_manager import RiskManager
from order_manager import OrderManager
from live_trader import LiveTrader
from logger import Logger

logger = Logger(__name__)

    # Instantiate Binance client with API key and secret from config
try:
    binance = Binance(Config.API_KEY, Config.API_SECRET)
except Exception as e:
    logger.error(f"Error connecting to Binance: {e}")

    # Instantiate trading strategy with EMA and MACD parameters from config
try:
    df = binance.fetch_candles(Config.TRADING_PAIRS[0], Config.TIMEFRAME, Config.LIMIT)
    strategy = Strategy(df, Config.EMA_FAST, Config.EMA_SLOW, Config.MACD_FAST, Config.MACD_SLOW, Config.MACD_SIGNAL)
except Exception as e:
    logger.error(f"Error Running Strategy: {e}")

    # Instantiate portfolio manager with trading fee rate from config
try:
    portfolio_manager = PortfolioManager(binance, Config.FEE_RATE)
except Exception as e:
    logger.error(f"Error Running PortfolioManager: {e}")

    # Instantiate risk manager with stop loss, take profit, and risk factor parameters from config
try:
    risk_manager = RiskManager(portfolio_manager, Config.STOP_LOSS_PERCENTAGE, Config.TAKE_PROFIT_PERCENTAGE, Config.RISK_FACTOR_PERCENTAGE)
except Exception as e:
    logger.error(f"Error Running RiskManager: {e}")

    # Instantiate order manager
try:
    order_manager = OrderManager(binance, portfolio_manager, risk_manager)
except Exception as e:
    logger.error(f"Error Running OrderManager: {e}")

    # Instantiate live trader with trading pairs, time frame, and candle limit from config
try:
    trader = LiveTrader(strategy, order_manager, risk_manager, Config.TRADING_PAIRS, Config.TIMEFRAME, Config.LIMIT, Config.TAKE_PROFIT_PERCENTAGE)

    # Run live trader
    trader.run()
except Exception as e:
    logger.error(f"Error Running LiveTrader: {e}")
