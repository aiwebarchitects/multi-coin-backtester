"""
Stochastic Oscillator Algorithm Implementation
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class StochasticAlgorithm(BaseAlgorithm):
    """Stochastic Oscillator trading algorithm implementation"""
    
    def __init__(self, k_period: int = 14, d_period: int = 3, 
                 oversold_threshold: int = 20, overbought_threshold: int = 80, **kwargs):
        super().__init__("STOCHASTIC", **kwargs)
        self.k_period = k_period
        self.d_period = d_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def calculate_stochastic(self, prices: pd.Series) -> tuple:
        """
        Calculate Stochastic Oscillator (%K and %D)
        
        %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
        %D = SMA of %K
        
        Returns:
            tuple: (k_values, d_values)
        """
        # Calculate rolling high and low
        rolling_high = prices.rolling(window=self.k_period).max()
        rolling_low = prices.rolling(window=self.k_period).min()
        
        # Calculate %K (Fast Stochastic)
        k_values = ((prices - rolling_low) / (rolling_high - rolling_low)) * 100
        
        # Calculate %D (Slow Stochastic - SMA of %K)
        d_values = k_values.rolling(window=self.d_period).mean()
        
        return k_values, d_values
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate Stochastic Oscillator trading signals
        
        Strategy:
        - Buy when %K crosses above %D in oversold territory (< oversold_threshold)
        - Sell when %K crosses below %D in overbought territory (> overbought_threshold)
        
        Alternative signals:
        - Buy when %K crosses above oversold threshold
        - Sell when %K crosses below overbought threshold
        """
        k_values, d_values = self.calculate_stochastic(data['price'])
        signals = pd.Series(0, index=data.index)
        
        # Strategy 1: %K crosses above %D in oversold territory (bullish crossover)
        buy_condition = (
            (k_values > d_values) & 
            (k_values.shift(1) <= d_values.shift(1)) &
            (k_values < self.oversold_threshold + 10)  # Near or in oversold
        )
        
        # Strategy 2: %K crosses below %D in overbought territory (bearish crossover)
        sell_condition = (
            (k_values < d_values) & 
            (k_values.shift(1) >= d_values.shift(1)) &
            (k_values > self.overbought_threshold - 10)  # Near or in overbought
        )
        
        signals[buy_condition] = 1   # Buy signal
        signals[sell_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic indicators and add to data"""
        result = data.copy()
        k_values, d_values = self.calculate_stochastic(data['price'])
        
        result['stoch_k'] = k_values
        result['stoch_d'] = d_values
        result['stoch_diff'] = k_values - d_values
        
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for Stochastic optimization"""
        return {
            'k_period': [10, 14, 20],
            'd_period': [3, 5, 7],
            'oversold_threshold': [15, 20, 25, 30],
            'overbought_threshold': [70, 75, 80, 85]
        }
    
    def __str__(self):
        return f"Stochastic(k_period={self.k_period}, d_period={self.d_period}, oversold={self.oversold_threshold}, overbought={self.overbought_threshold})"
