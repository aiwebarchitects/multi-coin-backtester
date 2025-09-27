"""
SMA (Simple Moving Average) Algorithm Implementation
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class SMAAlgorithm(BaseAlgorithm):
    """Simple Moving Average trading algorithm implementation"""
    
    def __init__(self, short_period: int = 10, long_period: int = 20, **kwargs):
        super().__init__("SMA", **kwargs)
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_sma(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calculate Simple Moving Averages"""
        # Calculate short and long period SMAs
        short_sma = prices.rolling(window=self.short_period, min_periods=self.short_period).mean()
        long_sma = prices.rolling(window=self.long_period, min_periods=self.long_period).mean()
        
        return {
            'short_sma': short_sma,
            'long_sma': long_sma
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate SMA trading signals
        
        Strategy:
        - Buy when short SMA crosses above long SMA (golden cross)
        - Sell when short SMA crosses below long SMA (death cross)
        """
        sma_data = self.calculate_sma(data['price'])
        short_sma = sma_data['short_sma']
        long_sma = sma_data['long_sma']
        
        signals = pd.Series(0, index=data.index)
        
        # Generate buy signals (short SMA crosses above long SMA)
        buy_condition = (
            (short_sma > long_sma) & 
            (short_sma.shift(1) <= long_sma.shift(1))
        )
        
        # Generate sell signals (short SMA crosses below long SMA)
        sell_condition = (
            (short_sma < long_sma) & 
            (short_sma.shift(1) >= long_sma.shift(1))
        )
        
        signals[buy_condition] = 1   # Buy signal
        signals[sell_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA indicators and add to data"""
        result = data.copy()
        sma_data = self.calculate_sma(data['price'])
        
        result['short_sma'] = sma_data['short_sma']
        result['long_sma'] = sma_data['long_sma']
        
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for SMA optimization"""
        return {
            'short_period': [5, 8, 10, 12, 15],
            'long_period': [20, 25, 30, 35, 40]
        }
    
    def __str__(self):
        return f"SMA(short={self.short_period}, long={self.long_period})"
