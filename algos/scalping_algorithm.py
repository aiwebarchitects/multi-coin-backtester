"""
Scalping Algorithm Implementation
A short-term trading strategy that aims to profit from small price movements
"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_algorithm import BaseAlgorithm


class ScalpingAlgorithm(BaseAlgorithm):
    """
    Scalping trading algorithm implementation
    
    This algorithm uses multiple indicators for quick entry/exit decisions:
    - EMA crossover for trend direction
    - RSI for momentum confirmation
    - Volume spike detection for entry timing
    """
    
    def __init__(self, fast_ema: int = 5, slow_ema: int = 13, 
                 rsi_period: int = 7, rsi_oversold: int = 30, 
                 rsi_overbought: int = 70, volume_multiplier: float = 1.5, **kwargs):
        super().__init__("Scalping", **kwargs)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.volume_multiplier = volume_multiplier
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.ewm(span=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.rsi_period, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def detect_volume_spike(self, volume: pd.Series) -> pd.Series:
        """Detect volume spikes above average"""
        avg_volume = volume.rolling(window=20, min_periods=1).mean()
        volume_spike = volume > (avg_volume * self.volume_multiplier)
        return volume_spike
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate scalping trading signals
        
        Strategy:
        - Long Entry: Fast EMA crosses above Slow EMA + RSI > oversold + Volume spike
        - Short Entry: Fast EMA crosses below Slow EMA + RSI < overbought + Volume spike
        
        This is designed for quick trades with tight stop losses and take profits
        """
        # Calculate indicators
        fast_ema = self.calculate_ema(data['price'], self.fast_ema)
        slow_ema = self.calculate_ema(data['price'], self.slow_ema)
        rsi = self.calculate_rsi(data['price'])
        volume_spike = self.detect_volume_spike(data['volume'])
        
        signals = pd.Series(0, index=data.index)
        
        # EMA crossover conditions
        bullish_cross = (fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))
        bearish_cross = (fast_ema < slow_ema) & (fast_ema.shift(1) >= slow_ema.shift(1))
        
        # Long signal: Bullish EMA cross + RSI not overbought + Volume spike
        long_condition = (
            bullish_cross & 
            (rsi > self.rsi_oversold) & 
            (rsi < self.rsi_overbought) &
            volume_spike
        )
        
        # Short signal: Bearish EMA cross + RSI not oversold + Volume spike
        short_condition = (
            bearish_cross & 
            (rsi < self.rsi_overbought) & 
            (rsi > self.rsi_oversold) &
            volume_spike
        )
        
        signals[long_condition] = 1   # Buy signal
        signals[short_condition] = -1  # Sell signal
        
        return signals
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all scalping indicators and add to data"""
        result = data.copy()
        result['fast_ema'] = self.calculate_ema(data['price'], self.fast_ema)
        result['slow_ema'] = self.calculate_ema(data['price'], self.slow_ema)
        result['rsi'] = self.calculate_rsi(data['price'])
        result['volume_spike'] = self.detect_volume_spike(data['volume'])
        return result
    
    def get_parameter_ranges(self) -> Dict:
        """Get parameter ranges for scalping optimization"""
        return {
            'fast_ema': [3, 5, 8],
            'slow_ema': [10, 13, 15, 20],
            'rsi_period': [5, 7, 9],
            'rsi_oversold': [25, 30, 35],
            'rsi_overbought': [65, 70, 75],
            'volume_multiplier': [1.3, 1.5, 1.8, 2.0]
        }
    
    def __str__(self):
        return (f"Scalping(fast_ema={self.fast_ema}, slow_ema={self.slow_ema}, "
                f"rsi_period={self.rsi_period}, rsi_oversold={self.rsi_oversold}, "
                f"rsi_overbought={self.rsi_overbought}, volume_mult={self.volume_multiplier})")
