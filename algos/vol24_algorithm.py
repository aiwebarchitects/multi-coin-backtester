"""
Volume 24h Algorithm Implementation
Identifies volume spikes and price momentum for trading signals
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class Vol24Algorithm(BaseAlgorithm):
    """Volume 24h trading algorithm implementation"""
    
    def __init__(self, volume_period: int = 24, volume_spike_threshold: float = 1.5, 
                 price_change_threshold: float = 0.002, **kwargs):
        super().__init__("VOL24", **kwargs)
        self.volume_period = volume_period
        self.volume_spike_threshold = volume_spike_threshold
        self.price_change_threshold = price_change_threshold
    
    def calculate_volume_metrics(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volume-based metrics"""
        # Volume moving average
        volume_ma = data['volume'].rolling(window=self.volume_period).mean()
        
        # Volume ratio (current volume vs average)
        volume_ratio = data['volume'] / volume_ma
        
        # Volume spike detection
        volume_spike = volume_ratio >= self.volume_spike_threshold
        
        # Price change over the period
        price_change = data['price'].pct_change(periods=self.volume_period)
        
        # Price momentum (rate of change)
        price_momentum = data['price'].pct_change()
        
        return {
            'volume_ma': volume_ma,
            'volume_ratio': volume_ratio,
            'volume_spike': volume_spike,
            'price_change': price_change,
            'price_momentum': price_momentum
        }
    
    def detect_breakout_pattern(self, data: pd.DataFrame, metrics: Dict) -> pd.Series:
        """Detect volume breakout patterns"""
        breakout_signals = pd.Series(False, index=data.index)
        
        # Look for volume spikes with significant price movement
        volume_condition = metrics['volume_spike']
        price_condition = abs(metrics['price_momentum']) >= self.price_change_threshold
        
        # Combine conditions
        breakout_signals = volume_condition & price_condition
        
        return breakout_signals
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate Volume 24h trading signals
        
        Strategy:
        - Buy when volume spike occurs with upward price momentum
        - Sell when volume spike occurs with downward price momentum
        """
        metrics = self.calculate_volume_metrics(data)
        breakout_signals = self.detect_breakout_pattern(data, metrics)
        
        signals = pd.Series(0, index=data.index)
        
        for i in range(1, len(data)):
            if not breakout_signals.iloc[i]:
                continue
            
            current_momentum = metrics['price_momentum'].iloc[i]
            volume_spike = metrics['volume_spike'].iloc[i]
            
            # Additional confirmation: check if volume is significantly above average
            if volume_spike and abs(current_momentum) >= self.price_change_threshold:
                if current_momentum > 0:
                    # Upward momentum with volume spike = Buy signal
                    signals.iloc[i] = 1
                else:
                    # Downward momentum with volume spike = Sell signal
                    signals.iloc[i] = -1
        
        return signals
    
    def calculate_volume_strength(self, data: pd.DataFrame) -> pd.Series:
        """Calculate volume strength indicator"""
        metrics = self.calculate_volume_metrics(data)
        
        # Combine volume ratio and price momentum for strength score
        volume_strength = (
            metrics['volume_ratio'] * 
            abs(metrics['price_momentum']) * 100
        )
        
        return volume_strength
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume indicators and add to data"""
        result = data.copy()
        metrics = self.calculate_volume_metrics(data)
        
        result['volume_ma'] = metrics['volume_ma']
        result['volume_ratio'] = metrics['volume_ratio']
        result['volume_spike'] = metrics['volume_spike']
        result['price_change'] = metrics['price_change']
        result['price_momentum'] = metrics['price_momentum']
        result['volume_strength'] = self.calculate_volume_strength(data)
        result['breakout_pattern'] = self.detect_breakout_pattern(data, metrics)
        
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for Vol24 optimization"""
        return {
            'volume_period': [20, 24, 30],
            'volume_spike_threshold': [2.0, 3.0, 4.0],
            'price_change_threshold': [0.005, 0.01, 0.015]
        }
    
    def __str__(self):
        return f"Vol24(period={self.volume_period}, spike_threshold={self.volume_spike_threshold}, price_threshold={self.price_change_threshold})"
