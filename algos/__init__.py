"""
Algorithms package for the multi-crypto backtesting system
"""

from .base_algorithm import BaseAlgorithm, BacktestEngine
from .rsi_algorithm import RSIAlgorithm
from .macd_algorithm import MACDAlgorithm
from .support_volume_algorithm import SupportVolumeAlgorithm
from .vol24_algorithm import Vol24Algorithm
from .sma_algorithm import SMAAlgorithm

__all__ = ['BaseAlgorithm', 'BacktestEngine', 'RSIAlgorithm', 'MACDAlgorithm', 
           'SupportVolumeAlgorithm', 'Vol24Algorithm', 'SMAAlgorithm', 'AlgorithmFactory']


class AlgorithmFactory:
    """Factory class for creating algorithm instances"""
    
    @staticmethod
    def create_algorithm(name: str, **params):
        """Create an algorithm instance by name"""
        algorithms = {
            'RSI': RSIAlgorithm,
            'MACD': MACDAlgorithm,
            'SUPPORT_VOLUME': SupportVolumeAlgorithm,
            'VOL24': Vol24Algorithm,
            'SMA': SMAAlgorithm
        }
        
        if name not in algorithms:
            raise ValueError(f"Unknown algorithm: {name}. Available: {list(algorithms.keys())}")
        
        return algorithms[name](**params)
    
    @staticmethod
    def get_available_algorithms():
        """Get list of available algorithm names"""
        return ['RSI', 'MACD', 'SUPPORT_VOLUME', 'VOL24', 'SMA']
