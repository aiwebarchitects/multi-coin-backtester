"""
Settings configuration for the multi-algorithm backtesting system
"""

# Coins to backtest (starting with BTC and ETH as requested)
COINS = ["BTC", "ETH"]

# Timeframe for backtesting (minute data for short-term trading)
TIMEFRAME = "1m"

# Data settings
DATA_DIR = "data"
RESULTS_DIR = "results"

# Backtesting parameters
INITIAL_BALANCE = 10000  # Starting balance in USD
COMMISSION_RATE = 0.001  # 0.1% commission per trade

# Algorithm settings
ALGORITHMS = [
    "MACD",
    "RSI",
    "SUPPORT_VOLUME",
    "VOL24",
    "SMA"
]

# MACD algorithm parameter ranges for optimization (reduced for faster testing)
MACD_PARAMS = {
    'fast_period': [10, 12, 14],
    'slow_period': [24, 26, 28],
    'signal_period': [8, 9, 10],
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# RSI algorithm parameter ranges for optimization (reduced for faster testing)
RSI_PARAMS = {
    'period': [12, 14, 16],
    'oversold_threshold': [25, 30, 35],
    'overbought_threshold': [65, 70, 75],
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# Support and Volume algorithm parameter ranges
SUPPORT_VOLUME_PARAMS = {
    'support_period': [10, 15, 20],
    'volume_threshold': [1.2, 1.5, 2.0],  # Volume multiplier
    'min_touches': [2, 3, 4],  # Minimum support level touches
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# Volume 24h algorithm parameter ranges
VOL24_PARAMS = {
    'volume_period': [20, 24, 30],  # Period for volume average
    'volume_spike_threshold': [2.0, 3.0, 4.0],  # Volume spike multiplier
    'price_change_threshold': [0.005, 0.01, 0.015],  # Minimum price change
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# SMA algorithm parameter ranges
SMA_PARAMS = {
    'short_period': [5, 8, 10, 12, 15],  # Short moving average period
    'long_period': [20, 25, 30, 35, 40],  # Long moving average period
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# Minimum number of trades required for valid backtest results
MIN_TRADES_THRESHOLD = 3

# Output settings
SAVE_PLOTS = False  # Set to True to enable plotting (disabled for performance)
VERBOSE = True  # Set to False to reduce output
