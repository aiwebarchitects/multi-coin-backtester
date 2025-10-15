"""
Settings configuration for the multi-algorithm backtesting system
"""

# Coins to backtest (starting with BTC and ETH as requested)
#COINS = ["BTC", "ETH", "LTC", "XRP", "ADA", "SOL"]

COINS = ["PAXG"]

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
    "RSI_4H",
    "RSI_1MIN_DOUBLE_CONFIRM",
    "RSI_4H_DOUBLE_CONFIRM",
    "RSI_5MIN_DOUBLE_CONFIRM",
    "SUPPORT_VOLUME",
    "VOL24",
    "SMA",
    "SCALPING",
    "BOLLINGER_BANDS",
    "STOCHASTIC"
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
    'oversold_threshold': [15, 20, 25, 30, 35],
    'overbought_threshold': [65, 70, 75, 80, 85],
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# RSI 4H algorithm parameter ranges for optimization (optimized for 4-hour candles)
RSI_4H_PARAMS = {
    'period': [14, 16, 18, 20, 24, 28],
    'oversold_threshold': [20, 25, 30, 35],
    'overbought_threshold': [65, 70, 75, 80],
    'take_profit': [0.02, 0.03, 0.04, 0.05],  # 2% to 5% (larger for 4h timeframe)
    'stop_loss': [-0.01, -0.015, -0.02]  # -1% to -2% (larger for 4h timeframe)
}

# RSI 1MIN Double Confirm algorithm parameter ranges (requires 2 consecutive oversold signals on 1-minute)
RSI_1MIN_DOUBLE_CONFIRM_PARAMS = {
    'period': [10, 12, 14, 16, 18, 20],
    'oversold_threshold': [15, 20, 25, 30, 35],
    'overbought_threshold': [65, 70, 75, 80, 85],
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# RSI 4H Double Confirm algorithm parameter ranges (requires 2 consecutive oversold signals on 4-hour)
RSI_4H_DOUBLE_CONFIRM_PARAMS = {
    'period': [14, 16, 18, 20, 24, 28],
    'oversold_threshold': [20, 25, 30, 35],
    'overbought_threshold': [65, 70, 75, 80],
    'take_profit': [0.02, 0.03, 0.04, 0.05],  # 2% to 5% (larger for 4h timeframe)
    'stop_loss': [-0.01, -0.015, -0.02]  # -1% to -2% (larger for 4h timeframe)
}

# RSI 5MIN Double Confirm algorithm parameter ranges (requires 2 consecutive oversold signals on 5-minute)
RSI_5MIN_DOUBLE_CONFIRM_PARAMS = {
    'period': [10, 12, 14, 16, 18, 20],
    'oversold_threshold': [20, 25, 30, 35],
    'overbought_threshold': [65, 70, 75, 80],
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2% (moderate for 5min timeframe)
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1% (moderate for 5min timeframe)
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

# Scalping algorithm parameter ranges (optimized for quick trades)
SCALPING_PARAMS = {
    'fast_ema': [3, 5, 8],  # Fast EMA period
    'slow_ema': [10, 13, 15, 20],  # Slow EMA period
    'rsi_period': [5, 7, 9],  # RSI period for momentum
    'rsi_oversold': [25, 30, 35],  # RSI oversold threshold
    'rsi_overbought': [65, 70, 75],  # RSI overbought threshold
    'volume_multiplier': [1.3, 1.5, 1.8, 2.0],  # Volume spike multiplier
    'take_profit': [0.005, 0.008, 0.01, 0.012],  # 0.5% to 1.2% (tighter for scalping)
    'stop_loss': [-0.003, -0.005, -0.007]  # -0.3% to -0.7% (tighter for scalping)
}

# Bollinger Bands algorithm parameter ranges
BOLLINGER_BANDS_PARAMS = {
    'period': [10, 15, 20, 25, 30],  # Moving average period
    'std_dev': [1.5, 2.0, 2.5, 3.0],  # Standard deviation multiplier
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# Stochastic Oscillator algorithm parameter ranges
STOCHASTIC_PARAMS = {
    'k_period': [10, 14, 20],  # %K period (fast stochastic)
    'd_period': [3, 5, 7],  # %D period (slow stochastic - SMA of %K)
    'oversold_threshold': [15, 20, 25, 30],  # Oversold threshold
    'overbought_threshold': [70, 75, 80, 85],  # Overbought threshold
    'take_profit': [0.01, 0.015, 0.02],  # 1% to 2%
    'stop_loss': [-0.005, -0.007, -0.01]  # -0.5% to -1%
}

# Minimum number of trades required for valid backtest results
MIN_TRADES_THRESHOLD = 3

# Output settings
SAVE_PLOTS = True  # Set to True to enable plotting (disabled for performance)
VERBOSE = True  # Set to False to reduce output

# =============================================================================
# COIN MAPPINGS - DO NOT MODIFY
# =============================================================================
# Comprehensive mapping of coin symbols to CoinGecko API IDs
# This is a reference mapping - only coins in COINS list above will be processed
COIN_MAPPINGS = {
    # Top cryptocurrencies by market cap
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'USDC': 'usd-coin',
    'XRP': 'ripple',
    'DOGE': 'dogecoin',
    'TON': 'the-open-network',
    'ADA': 'cardano',
    'SHIB': 'shiba-inu',
    'AVAX': 'avalanche-2',
    'TRX': 'tron',
    'DOT': 'polkadot',
    'BCH': 'bitcoin-cash',
    'LINK': 'chainlink',
    'NEAR': 'near',
    'MATIC': 'matic-network',
    'ICP': 'internet-computer',
    'LTC': 'litecoin',
    'UNI': 'uniswap',
    'LEO': 'leo-token',
    'DAI': 'dai',
    'ETC': 'ethereum-classic',
    'APT': 'aptos',
    'ATOM': 'cosmos',
    'XMR': 'monero',
    'STX': 'stacks',
    'OKB': 'okb',
    'FIL': 'filecoin',
    'ARB': 'arbitrum',
    'IMX': 'immutable-x',
    'VET': 'vechain',
    'MNT': 'mantle',
    'HBAR': 'hedera-hashgraph',
    'OP': 'optimism',
    'INJ': 'injective-protocol',
    'MKR': 'maker',
    'AAVE': 'aave',
    'GRT': 'the-graph',
    'THETA': 'theta-token',
    'RUNE': 'thorchain',
    'ALGO': 'algorand',
    'FLOW': 'flow',
    'EGLD': 'elrond-erd-2',
    'SAND': 'the-sandbox',
    'MANA': 'decentraland',
    'AXS': 'axie-infinity',
    'XTZ': 'tezos',
    'KLAY': 'klay-token',
    'FTM': 'fantom',
    'PAXG': 'pax-gold',
    'CRV': 'curve-dao-token',
    'LDO': 'lido-dao',
    'QNT': 'quant-network',
    'COMP': 'compound-governance-token',
    'SNX': 'havven',
    'SUSHI': 'sushi',
    'YFI': 'yearn-finance',
    'BAT': 'basic-attention-token',
    'ZRX': '0x',
    'ENJ': 'enjincoin',
    'CHZ': 'chiliz',
    'MANA': 'decentraland',
    '1INCH': '1inch',
    'STORJ': 'storj',
    'REN': 'republic-protocol',
    'KNC': 'kyber-network-crystal',
    'ZIL': 'zilliqa',
    'ICX': 'icon',
    'ONT': 'ontology',
    'QTUM': 'qtum',
    'ZEC': 'zcash',
    'DASH': 'dash',
    'WAVES': 'waves',
    'DCR': 'decred',
    'LSK': 'lisk',
    'NANO': 'nano',
    'DGB': 'digibyte',
    'SC': 'siacoin',
    'ZEN': 'zencash',
    'DOGE': 'dogecoin',
    'RVN': 'ravencoin'
}
