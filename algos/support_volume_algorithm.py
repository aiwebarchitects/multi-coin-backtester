"""
Support and Volume Algorithm Implementation
Identifies support levels and volume confirmation for trading signals
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class SupportVolumeAlgorithm(BaseAlgorithm):
    """Support and Volume trading algorithm implementation"""
    
    def __init__(self, support_period: int = 20, volume_threshold: float = 1.5, 
                 min_touches: int = 3, **kwargs):
        super().__init__("SUPPORT_VOLUME", **kwargs)
        self.support_period = support_period
        self.volume_threshold = volume_threshold
        self.min_touches = min_touches
    
    def find_support_levels(self, data: pd.DataFrame) -> pd.Series:
        """Find support levels based on local minima"""
        prices = data['price']
        support_levels = pd.Series(np.nan, index=data.index)
        
        # Find local minima (potential support levels)
        for i in range(self.support_period, len(prices) - self.support_period):
            window = prices.iloc[i-self.support_period:i+self.support_period+1]
            if prices.iloc[i] == window.min():
                # Check if this level has been touched multiple times
                level_price = prices.iloc[i]
                tolerance = level_price * 0.002  # 0.2% tolerance
                
                # Count touches within tolerance
                touches = 0
                for j in range(max(0, i-100), min(len(prices), i+100)):
                    if abs(prices.iloc[j] - level_price) <= tolerance:
                        touches += 1
                
                if touches >= self.min_touches:
                    support_levels.iloc[i] = level_price
        
        # Forward fill support levels
        support_levels = support_levels.ffill()
        
        return support_levels
    
    def calculate_volume_confirmation(self, data: pd.DataFrame) -> pd.Series:
        """Calculate volume confirmation signals"""
        volume_ma = data['volume'].rolling(window=self.support_period).mean()
        volume_ratio = data['volume'] / volume_ma
        
        # Volume spike confirmation
        volume_spike = volume_ratio >= self.volume_threshold
        
        return volume_spike
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate Support and Volume trading signals
        
        Strategy:
        - Buy when price bounces off support level with volume confirmation
        - Sell when price breaks below support level with volume confirmation
        """
        support_levels = self.find_support_levels(data)
        volume_confirmation = self.calculate_volume_confirmation(data)
        
        signals = pd.Series(0, index=data.index)
        
        for i in range(1, len(data)):
            current_price = data['price'].iloc[i]
            prev_price = data['price'].iloc[i-1]
            support_level = support_levels.iloc[i]
            has_volume = volume_confirmation.iloc[i]
            
            if pd.isna(support_level):
                continue
            
            # Buy signal: price bounces off support with volume
            if (prev_price <= support_level * 1.005 and  # Was near support
                current_price > support_level * 1.005 and  # Now above support
                has_volume):  # With volume confirmation
                signals.iloc[i] = 1
            
            # Sell signal: price breaks below support with volume
            elif (prev_price >= support_level * 0.995 and  # Was above support
                  current_price < support_level * 0.995 and  # Now below support
                  has_volume):  # With volume confirmation
                signals.iloc[i] = -1
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate support and volume indicators and add to data"""
        result = data.copy()
        result['support_level'] = self.find_support_levels(data)
        result['volume_confirmation'] = self.calculate_volume_confirmation(data)
        result['volume_ma'] = data['volume'].rolling(window=self.support_period).mean()
        result['volume_ratio'] = data['volume'] / result['volume_ma']
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for Support Volume optimization"""
        return {
            'support_period': [10, 15, 20],
            'volume_threshold': [1.2, 1.5, 2.0],
            'min_touches': [2, 3, 4]
        }
    
    def __str__(self):
        return f"SupportVolume(period={self.support_period}, vol_threshold={self.volume_threshold}, min_touches={self.min_touches})"
