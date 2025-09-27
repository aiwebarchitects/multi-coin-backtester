# Multi-Crypto Multi-Algorithm Backtester

A modular, self-testing cryptocurrency backtesting system that automatically finds the best trading algorithms for short-term crypto trading with the highest total profit.

## 🚀 Features

- **Modular Architecture**: Easy to add new trading algorithms
- **Self-Testing**: Automatically optimizes parameters for each algorithm
- **Multiple Algorithms**: MACD, RSI, Support & Volume, Volume 24h, SMA
- **Real-Time Data**: Downloads fresh minute-level historical data
- **Performance Ranking**: Automatically ranks strategies by total profit
- **Minimum Trades Filter**: Only saves strategies with sufficient trade volume
- **Comprehensive Metrics**: Win rate, profit factor, drawdown, and more

## 📊 Supported Algorithms

1. **MACD (Moving Average Convergence Divergence)**
   - Fast/slow period optimization
   - Signal line crossover strategy
   - Configurable take profit/stop loss

2. **RSI (Relative Strength Index)**
   - Overbought/oversold threshold optimization
   - Period length optimization
   - Momentum-based entry/exit signals

3. **Support & Volume**
   - Support level identification
   - Volume confirmation signals
   - Multi-touch validation

4. **Volume 24h**
   - Volume spike detection
   - Price momentum confirmation
   - Breakout pattern recognition

5. **SMA (Simple Moving Average)**
   - Short/long period moving average crossover
   - Golden cross and death cross signals
   - Trend-following strategy

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/aiwebarchitects/multi-coin-backtester.git
cd multi-coin-backtester
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Quick Start
Run the complete backtesting system:
```bash
python3 start_backtesting.py
```

The system will:
1. Download historical minute data for BTC and ETH
2. Test all algorithms with parameter optimization
3. Display the best strategies ranked by total profit
4. Save results to `results/best_results.json`

### Configuration

Edit `settings.py` to customize:

```python
# Coins to backtest
COINS = ["BTC", "ETH"]  # Add more coins here

# Algorithms to test
ALGORITHMS = [
    "MACD",
    "RSI", 
    "SUPPORT_VOLUME",
    "VOL24",
    "SMA"
]

# Timeframe for trading
TIMEFRAME = "1m"  # 1-minute candles for short-term trading

# Minimum trades required for valid results
MIN_TRADES_THRESHOLD = 3
```

### Parameter Ranges

Each algorithm has configurable parameter ranges in `settings.py`:

```python
# Example: MACD parameters
MACD_PARAMS = {
    'fast_period': [10, 12, 14],
    'slow_period': [24, 26, 28], 
    'signal_period': [8, 9, 10],
    'take_profit': [0.01, 0.015, 0.02],
    'stop_loss': [-0.005, -0.007, -0.01]
}
```

## 📈 Example Results

```
🏆 BEST OVERALL STRATEGY:
Algorithm: SMA
Coin: ETH
Win Rate: 100.00%
Total Trades: 7
Total Profit: 6.34%
Profit Factor: inf

📊 ALL STRATEGIES RANKED BY TOTAL PROFIT:
1. SMA  | ETH | Win Rate: 100.00% | Trades: 7 | Profit: 6.34%
2. RSI  | ETH | Win Rate: 100.00% | Trades: 7 | Profit: 6.16%
3. MACD | ETH | Win Rate:  90.91% | Trades: 11 | Profit: 6.05%
```

## 🔧 Adding a New Algorithm

### Step 1: Create Algorithm Class

Create a new file in the `algos/` directory (e.g., `algos/my_algorithm.py`):

```python
"""
My Custom Algorithm Implementation
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class MyAlgorithm(BaseAlgorithm):
    """My custom trading algorithm implementation"""
    
    def __init__(self, param1: int = 10, param2: float = 0.5, **kwargs):
        super().__init__("MY_ALGORITHM", **kwargs)
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from price data
        
        Returns:
            Series with trading signals: 1 for buy, -1 for sell, 0 for hold
        """
        signals = pd.Series(0, index=data.index)
        
        # Your algorithm logic here
        # Example: Simple moving average crossover
        short_ma = data['price'].rolling(window=self.param1).mean()
        long_ma = data['price'].rolling(window=self.param1 * 2).mean()
        
        # Buy when short MA crosses above long MA
        buy_condition = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        signals[buy_condition] = 1
        
        # Sell when short MA crosses below long MA  
        sell_condition = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        signals[sell_condition] = -1
        
        return signals
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for optimization"""
        return {
            'param1': [5, 10, 15, 20],
            'param2': [0.3, 0.5, 0.7, 1.0]
        }
    
    def __str__(self):
        return f"MyAlgorithm(param1={self.param1}, param2={self.param2})"
```

### Step 2: Register Algorithm

Add your algorithm to `algos/__init__.py`:

```python
from .my_algorithm import MyAlgorithm

# Add to __all__
__all__ = ['BaseAlgorithm', 'BacktestEngine', 'RSIAlgorithm', 'MACDAlgorithm', 
           'SupportVolumeAlgorithm', 'Vol24Algorithm', 'MyAlgorithm', 'AlgorithmFactory']

# Add to AlgorithmFactory
class AlgorithmFactory:
    @staticmethod
    def create_algorithm(name: str, **params):
        algorithms = {
            'RSI': RSIAlgorithm,
            'MACD': MACDAlgorithm,
            'SUPPORT_VOLUME': SupportVolumeAlgorithm,
            'VOL24': Vol24Algorithm,
            'MY_ALGORITHM': MyAlgorithm  # Add this line
        }
        # ... rest of the method
```

### Step 3: Add Configuration

Add parameter ranges to `settings.py`:

```python
# Add to ALGORITHMS list
ALGORITHMS = [
    "MACD",
    "RSI",
    "SUPPORT_VOLUME", 
    "VOL24",
    "MY_ALGORITHM"  # Add this line
]

# Add parameter configuration
MY_ALGORITHM_PARAMS = {
    'param1': [5, 10, 15, 20],
    'param2': [0.3, 0.5, 0.7, 1.0],
    'take_profit': [0.01, 0.015, 0.02],
    'stop_loss': [-0.005, -0.007, -0.01]
}
```

### Step 4: Update Parameter Optimizer

Add your algorithm to the parameter optimizer in `start_backtesting.py`:

```python
def get_parameter_combinations(self) -> List[Dict]:
    if self.algorithm_name == "RSI":
        param_ranges = settings.RSI_PARAMS
    elif self.algorithm_name == "MACD":
        param_ranges = settings.MACD_PARAMS
    elif self.algorithm_name == "SUPPORT_VOLUME":
        param_ranges = settings.SUPPORT_VOLUME_PARAMS
    elif self.algorithm_name == "VOL24":
        param_ranges = settings.VOL24_PARAMS
    elif self.algorithm_name == "MY_ALGORITHM":  # Add this
        param_ranges = settings.MY_ALGORITHM_PARAMS
    else:
        raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
```

### Step 5: Test Your Algorithm

Run the backtesting system to test your new algorithm:

```bash
python3 start_backtesting.py
```

## 📁 Project Structure

```
multi-coin-backtester/
├── start_backtesting.py          # Main entry point
├── settings.py                   # Configuration file
├── historical_data_fetcher.py    # Data download functionality
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── algos/                        # Algorithm implementations
│   ├── __init__.py              # Algorithm factory
│   ├── base_algorithm.py        # Base classes and backtest engine
│   ├── rsi_algorithm.py         # RSI implementation
│   ├── macd_algorithm.py        # MACD implementation
│   ├── support_volume_algorithm.py # Support & Volume implementation
│   ├── vol24_algorithm.py       # Volume 24h implementation
│   └── sma_algorithm.py         # SMA implementation
├── data/                         # Historical data storage
│   ├── BTC/                     # Bitcoin data
│   └── ETH/                     # Ethereum data
└── results/                      # Backtest results
    └── best_results.json        # Optimized strategy results
```

## ⚙️ Advanced Configuration

### Data Sources
The system uses:
- **CoinGecko API**: For 30-day OHLC data
- **CryptoCompare API**: For recent minute-level data

### Performance Metrics
Each strategy is evaluated on:
- **Win Rate**: Percentage of profitable trades
- **Total Profit**: Cumulative profit percentage
- **Profit Factor**: Ratio of gross profit to gross loss
- **Max Drawdown**: Maximum peak-to-trough decline
- **Average Trade Duration**: Mean time per trade

### Optimization Process
1. **Parameter Grid Search**: Tests all combinations of parameters
2. **Minimum Trade Filter**: Requires at least 3 trades for validity
3. **Total Profit Ranking**: Prioritizes strategies with highest total profit
4. **Statistical Validation**: Ensures sufficient sample size

## 🔍 Troubleshooting

### Common Issues

1. **No signals generated**: Algorithm parameters may be too restrictive
   - Solution: Adjust parameter ranges in `settings.py`

2. **Insufficient trades**: Minimum trade threshold too high
   - Solution: Lower `MIN_TRADES_THRESHOLD` in `settings.py`

3. **API rate limits**: Too many requests to data providers
   - Solution: Add delays between requests in `historical_data_fetcher.py`

### Debug Mode
Enable verbose output in `settings.py`:
```python
VERBOSE = True
```

## 📊 Performance Tips

1. **Reduce Parameter Combinations**: Limit ranges for faster optimization
2. **Use Shorter Data Periods**: Test with less historical data initially
3. **Parallel Processing**: Consider multiprocessing for large parameter grids
4. **Caching**: Store downloaded data to avoid repeated API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your algorithm following the guide above
4. Test thoroughly with different market conditions
5. Submit a pull request with documentation

## 📄 License

This project is open source. Please check the license file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Past performance does not guarantee future results. Always do your own research and never invest more than you can afford to lose.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

**Happy Trading! 🚀📈**
