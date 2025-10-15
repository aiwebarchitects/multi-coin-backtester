"""
RSI 4H (Relative Strength Index on 4-Hour Candles) Algorithm Implementation
Optimized for medium-term swing trading using 4-hour timeframe data
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class RSI4HAlgorithm(BaseAlgorithm):
    """RSI trading algorithm implementation for 4-hour candles"""
    
    def __init__(self, period: int = 14, oversold_threshold: int = 30, 
                 overbought_threshold: int = 70, **kwargs):
        super().__init__("RSI_4H", **kwargs)
        self.period = period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss using exponential moving average
        avg_gain = gain.ewm(span=self.period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.period, adjust=False).mean()
        
        # Calculate RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate RSI trading signals for 4-hour candles
        
        Strategy:
        - Buy when RSI crosses above oversold threshold (e.g., 30)
        - Sell when RSI crosses below overbought threshold (e.g., 70)
        
        Optimized for 4-hour timeframe with less noise than 1-minute data
        """
        rsi = self.calculate_rsi(data['price'])
        signals = pd.Series(0, index=data.index)
        
        # Generate buy signals (RSI crosses above oversold)
        buy_condition = (
            (rsi > self.oversold_threshold) & 
            (rsi.shift(1) <= self.oversold_threshold)
        )
        
        # Generate sell signals (RSI crosses below overbought)
        sell_condition = (
            (rsi < self.overbought_threshold) & 
            (rsi.shift(1) >= self.overbought_threshold)
        )
        
        signals[buy_condition] = 1   # Buy signal
        signals[sell_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator and add to data"""
        result = data.copy()
        result['rsi'] = self.calculate_rsi(data['price'])
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """
        Get parameter ranges for RSI 4H optimization
        
        Optimized for 4-hour timeframe:
        - Longer periods for smoother signals
        - Standard oversold/overbought thresholds
        """
        return {
            'period': [14, 16, 18, 20, 24, 28],
            'oversold_threshold': [20, 25, 30, 35],
            'overbought_threshold': [65, 70, 75, 80]
        }
    
    def __str__(self):
        return f"RSI_4H(period={self.period}, oversold={self.oversold_threshold}, overbought={self.overbought_threshold})"
