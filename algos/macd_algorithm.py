"""
MACD (Moving Average Convergence Divergence) Algorithm Implementation
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class MACDAlgorithm(BaseAlgorithm):
    """MACD trading algorithm implementation"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, 
                 signal_period: int = 9, **kwargs):
        super().__init__("MACD", **kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate_macd(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calculate MACD components"""
        # Calculate exponential moving averages
        fast_ema = prices.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line (EMA of MACD line)
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram,
            'fast_ema': fast_ema,
            'slow_ema': slow_ema
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate MACD trading signals
        
        Strategy:
        - Buy when MACD line crosses above signal line (bullish crossover)
        - Sell when MACD line crosses below signal line (bearish crossover)
        """
        macd_data = self.calculate_macd(data['price'])
        macd_line = macd_data['macd']
        signal_line = macd_data['signal']
        
        signals = pd.Series(0, index=data.index)
        
        # Generate buy signals (MACD crosses above signal)
        buy_condition = (
            (macd_line > signal_line) & 
            (macd_line.shift(1) <= signal_line.shift(1))
        )
        
        # Generate sell signals (MACD crosses below signal)
        sell_condition = (
            (macd_line < signal_line) & 
            (macd_line.shift(1) >= signal_line.shift(1))
        )
        
        signals[buy_condition] = 1   # Buy signal
        signals[sell_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicators and add to data"""
        result = data.copy()
        macd_data = self.calculate_macd(data['price'])
        
        result['macd'] = macd_data['macd']
        result['macd_signal'] = macd_data['signal']
        result['macd_histogram'] = macd_data['histogram']
        result['fast_ema'] = macd_data['fast_ema']
        result['slow_ema'] = macd_data['slow_ema']
        
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for MACD optimization"""
        return {
            'fast_period': [8, 10, 12, 14, 16],
            'slow_period': [20, 24, 26, 28, 32],
            'signal_period': [6, 8, 9, 10, 12]
        }
    
    def __str__(self):
        return f"MACD(fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period})"
