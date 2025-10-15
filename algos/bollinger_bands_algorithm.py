"""
Bollinger Bands Algorithm Implementation
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class BollingerBandsAlgorithm(BaseAlgorithm):
    """Bollinger Bands trading algorithm implementation"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, **kwargs):
        super().__init__("BOLLINGER_BANDS", **kwargs)
        self.period = period
        self.std_dev = std_dev
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> tuple:
        """
        Calculate Bollinger Bands
        
        Returns:
            tuple: (middle_band, upper_band, lower_band)
        """
        # Middle band is the simple moving average
        middle_band = prices.rolling(window=self.period).mean()
        
        # Calculate standard deviation
        rolling_std = prices.rolling(window=self.period).std()
        
        # Upper and lower bands
        upper_band = middle_band + (rolling_std * self.std_dev)
        lower_band = middle_band - (rolling_std * self.std_dev)
        
        return middle_band, upper_band, lower_band
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate Bollinger Bands trading signals
        
        Strategy:
        - Buy when price crosses below lower band (oversold condition)
        - Sell when price crosses above upper band (overbought condition)
        - Alternative: Buy when price bounces off lower band, sell when it bounces off upper band
        """
        middle_band, upper_band, lower_band = self.calculate_bollinger_bands(data['price'])
        signals = pd.Series(0, index=data.index)
        
        # Calculate band width for volatility filter
        band_width = (upper_band - lower_band) / middle_band
        
        # Generate buy signals (price crosses below lower band)
        # This indicates oversold condition - potential reversal upward
        buy_condition = (
            (data['price'] < lower_band) & 
            (data['price'].shift(1) >= lower_band.shift(1)) &
            (band_width > 0.01)  # Ensure sufficient volatility
        )
        
        # Generate sell signals (price crosses above upper band)
        # This indicates overbought condition - potential reversal downward
        sell_condition = (
            (data['price'] > upper_band) & 
            (data['price'].shift(1) <= upper_band.shift(1)) &
            (band_width > 0.01)  # Ensure sufficient volatility
        )
        
        signals[buy_condition] = 1   # Buy signal
        signals[sell_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands indicators and add to data"""
        result = data.copy()
        middle_band, upper_band, lower_band = self.calculate_bollinger_bands(data['price'])
        
        result['bb_middle'] = middle_band
        result['bb_upper'] = upper_band
        result['bb_lower'] = lower_band
        result['bb_width'] = (upper_band - lower_band) / middle_band
        result['bb_position'] = (data['price'] - lower_band) / (upper_band - lower_band)
        
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for Bollinger Bands optimization"""
        return {
            'period': [10, 15, 20, 25, 30],
            'std_dev': [1.5, 2.0, 2.5, 3.0]
        }
    
    def __str__(self):
        return f"BollingerBands(period={self.period}, std_dev={self.std_dev})"
