"""
Algorithms package for the multi-crypto backtesting system
"""

from .base_algorithm import BaseAlgorithm, BacktestEngine
from .rsi_algorithm import RSIAlgorithm
from .rsi_4h_algorithm import RSI4HAlgorithm
from .rsi_1min_double_confirm_algorithm import RSI1MinDoubleConfirmAlgorithm
from .rsi_4h_double_confirm_algorithm import RSI4HDoubleConfirmAlgorithm
from .rsi_5min_double_confirm_algorithm import RSI5minDoubleConfirmAlgorithm
from .macd_algorithm import MACDAlgorithm
from .support_volume_algorithm import SupportVolumeAlgorithm
from .vol24_algorithm import Vol24Algorithm
from .sma_algorithm import SMAAlgorithm
from .scalping_algorithm import ScalpingAlgorithm
from .bollinger_bands_algorithm import BollingerBandsAlgorithm
from .stochastic_algorithm import StochasticAlgorithm

__all__ = ['BaseAlgorithm', 'BacktestEngine', 'RSIAlgorithm', 'RSI4HAlgorithm', 
           'RSI1MinDoubleConfirmAlgorithm', 'RSI4HDoubleConfirmAlgorithm', 
           'RSI5minDoubleConfirmAlgorithm', 'MACDAlgorithm', 
           'SupportVolumeAlgorithm', 'Vol24Algorithm', 'SMAAlgorithm', 'ScalpingAlgorithm',
           'BollingerBandsAlgorithm', 'StochasticAlgorithm', 'AlgorithmFactory']


class AlgorithmFactory:
    """Factory class for creating algorithm instances"""
    
    @staticmethod
    def create_algorithm(name: str, **params):
        """Create an algorithm instance by name"""
        algorithms = {
            'RSI': RSIAlgorithm,
            'RSI_4H': RSI4HAlgorithm,
            'RSI_1MIN_DOUBLE_CONFIRM': RSI1MinDoubleConfirmAlgorithm,
            'RSI_4H_DOUBLE_CONFIRM': RSI4HDoubleConfirmAlgorithm,
            'RSI_5MIN_DOUBLE_CONFIRM': RSI5minDoubleConfirmAlgorithm,
            'MACD': MACDAlgorithm,
            'SUPPORT_VOLUME': SupportVolumeAlgorithm,
            'VOL24': Vol24Algorithm,
            'SMA': SMAAlgorithm,
            'SCALPING': ScalpingAlgorithm,
            'BOLLINGER_BANDS': BollingerBandsAlgorithm,
            'STOCHASTIC': StochasticAlgorithm
        }
        
        if name not in algorithms:
            raise ValueError(f"Unknown algorithm: {name}. Available: {list(algorithms.keys())}")
        
        return algorithms[name](**params)
    
    @staticmethod
    def get_available_algorithms():
        """Get list of available algorithm names"""
        return ['RSI', 'RSI_4H', 'RSI_1MIN_DOUBLE_CONFIRM', 'RSI_4H_DOUBLE_CONFIRM', 'RSI_5MIN_DOUBLE_CONFIRM', 'MACD', 'SUPPORT_VOLUME', 'VOL24', 'SMA', 'SCALPING', 'BOLLINGER_BANDS', 'STOCHASTIC']
