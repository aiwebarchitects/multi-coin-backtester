"""
Main backtesting script for the multi-algorithm crypto backtesting system
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from itertools import product
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import settings and algorithms
import settings
from algos import AlgorithmFactory, BacktestEngine
from historical_data_fetcher import CryptoCompareHistoricalFetcher


class ParameterOptimizer:
    """Optimizer for finding best algorithm parameters"""
    
    def __init__(self, algorithm_name: str, data: pd.DataFrame, coin: str):
        self.algorithm_name = algorithm_name
        self.data = data
        self.coin = coin
        self.results = []
    
    def get_parameter_combinations(self) -> List[Dict]:
        """Get all parameter combinations for optimization"""
        if self.algorithm_name == "RSI":
            param_ranges = settings.RSI_PARAMS
        elif self.algorithm_name == "RSI_4H":
            param_ranges = settings.RSI_4H_PARAMS
        elif self.algorithm_name == "RSI_1MIN_DOUBLE_CONFIRM":
            param_ranges = settings.RSI_1MIN_DOUBLE_CONFIRM_PARAMS
        elif self.algorithm_name == "RSI_4H_DOUBLE_CONFIRM":
            param_ranges = settings.RSI_4H_DOUBLE_CONFIRM_PARAMS
        elif self.algorithm_name == "RSI_5MIN_DOUBLE_CONFIRM":
            param_ranges = settings.RSI_5MIN_DOUBLE_CONFIRM_PARAMS
        elif self.algorithm_name == "MACD":
            param_ranges = settings.MACD_PARAMS
        elif self.algorithm_name == "SUPPORT_VOLUME":
            param_ranges = settings.SUPPORT_VOLUME_PARAMS
        elif self.algorithm_name == "VOL24":
            param_ranges = settings.VOL24_PARAMS
        elif self.algorithm_name == "SMA":
            param_ranges = settings.SMA_PARAMS
        elif self.algorithm_name == "SCALPING":
            param_ranges = settings.SCALPING_PARAMS
        elif self.algorithm_name == "BOLLINGER_BANDS":
            param_ranges = settings.BOLLINGER_BANDS_PARAMS
        elif self.algorithm_name == "STOCHASTIC":
            param_ranges = settings.STOCHASTIC_PARAMS
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
        
        # Get algorithm-specific parameters
        algorithm = AlgorithmFactory.create_algorithm(self.algorithm_name)
        algo_ranges = algorithm.get_parameter_ranges()
        
        # Combine with take_profit and stop_loss
        all_ranges = {**algo_ranges, 
                     'take_profit': param_ranges['take_profit'],
                     'stop_loss': param_ranges['stop_loss']}
        
        # Generate all combinations
        keys = list(all_ranges.keys())
        values = list(all_ranges.values())
        combinations = []
        
        for combo in product(*values):
            param_dict = dict(zip(keys, combo))
            
            # Filter invalid combinations
            if self.algorithm_name == "MACD":
                if param_dict['fast_period'] >= param_dict['slow_period']:
                    continue
            elif self.algorithm_name == "SMA":
                if param_dict['short_period'] >= param_dict['long_period']:
                    continue
            elif self.algorithm_name == "SCALPING":
                if param_dict['fast_ema'] >= param_dict['slow_ema']:
                    continue
            
            combinations.append(param_dict)
        
        return combinations
    
    def optimize(self) -> Dict:
        """Run parameter optimization"""
        combinations = self.get_parameter_combinations()
        total_combinations = len(combinations)
        
        print(f"Testing {total_combinations} parameter combinations for {self.algorithm_name}...")
        
        best_result = {
            'total_profit': float('-inf'),
            'parameters': None,
            'metrics': None,
            'trades_df': None
        }
        
        for i, params in enumerate(combinations):
            if settings.VERBOSE and i % 50 == 0:
                print(f"Progress: {i+1}/{total_combinations} ({((i+1)/total_combinations)*100:.1f}%)")
            
            try:
                # Extract algorithm parameters and trading parameters
                algo_params = {k: v for k, v in params.items() 
                              if k not in ['take_profit', 'stop_loss']}
                
                # Create algorithm instance
                algorithm = AlgorithmFactory.create_algorithm(self.algorithm_name, **algo_params)
                
                # Create backtest engine
                engine = BacktestEngine(
                    algorithm=algorithm,
                    take_profit=params['take_profit'],
                    stop_loss=params['stop_loss'],
                    commission=settings.COMMISSION_RATE
                )
                
                # Run backtest
                trades_df, metrics = engine.backtest(self.data)
                
                # Store result
                result = {
                    **params,
                    'win_rate': metrics['win_rate'],
                    'total_trades': metrics['total_trades'],
                    'total_profit': metrics['total_profit'],
                    'profit_factor': metrics['profit_factor'],
                    'max_drawdown': metrics['max_drawdown'],
                    'avg_profit': metrics['avg_profit']
                }
                
                self.results.append(result)
                
                # Check if this is the best total profit so far
                if (metrics['total_profit'] > best_result['total_profit'] and 
                    metrics['total_trades'] >= settings.MIN_TRADES_THRESHOLD):
                    best_result = {
                        'total_profit': metrics['total_profit'],
                        'parameters': params,
                        'metrics': metrics,
                        'trades_df': trades_df
                    }
                    
            except Exception as e:
                if settings.VERBOSE:
                    print(f"Error with parameters {params}: {e}")
                continue
        
        print(f"Optimization complete! Best total profit: {best_result['total_profit']:.2f}%")
        return best_result


class BacktestingSystem:
    """Main backtesting system orchestrator"""
    
    def __init__(self):
        self.results = []
        self.data_fetcher = CryptoCompareHistoricalFetcher()
        
        # Create timestamp for this run (date + hour only)
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H")
        self.results_filepath = None
        
        # Ensure directories exist
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        os.makedirs(settings.RESULTS_DIR, exist_ok=True)
    
    def download_historical_data(self) -> bool:
        """Download historical data for all coins"""
        print("="*60)
        print("DOWNLOADING HISTORICAL DATA")
        print("="*60)
        
        try:
            success = self.data_fetcher.bootstrap_historical_data(
                base_data_dir=settings.DATA_DIR,
                coins=settings.COINS,
                use_coingecko=True
            )
            
            if success:
                print("✅ Historical data download completed successfully!")
                return True
            else:
                print("❌ Failed to download historical data")
                return False
                
        except Exception as e:
            print(f"❌ Error downloading data: {e}")
            return False
    
    def load_data(self, coin: str, algorithm_name: str = None) -> Optional[pd.DataFrame]:
        """Load historical data for a specific coin
        
        Args:
            coin: The coin symbol (e.g., 'BTC', 'ETH')
            algorithm_name: The algorithm name to determine timeframe (e.g., 'RSI_4H' uses 4h data)
        """
        try:
            # Determine timeframe based on algorithm
            if algorithm_name in ["RSI_4H", "RSI_4H_DOUBLE_CONFIRM"]:
                timeframe = "1h"  # 4-hour data is stored in 1h.json
            elif algorithm_name == "RSI_5MIN_DOUBLE_CONFIRM":
                timeframe = "5m"  # 5-minute data
            else:
                timeframe = settings.TIMEFRAME
            
            # Try to load data
            data_file = os.path.join(settings.DATA_DIR, coin, f"{timeframe}.json")
            
            if not os.path.exists(data_file):
                print(f"Data file not found: {data_file}")
                return None
            
            with open(data_file, 'r') as f:
                file_data = json.load(f)
            
            data_list = file_data.get('data', [])
            if not data_list:
                print(f"No data found in {data_file}")
                return None
            
            # Convert to DataFrame
            df_data = []
            for item in data_list:
                df_data.append({
                    'timestamp': pd.to_datetime(item['timestamp']),
                    'price': float(item['price']),
                    'volume': float(item['volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            df = df.sort_index()
            
            print(f"Loaded {len(df)} data points for {coin}")
            print(f"Data range: {df.index[0]} to {df.index[-1]}")
            
            return df
            
        except Exception as e:
            print(f"Error loading data for {coin}: {e}")
            return None
    
    def run_algorithm_backtest(self, algorithm_name: str, coin: str, data: pd.DataFrame) -> Dict:
        """Run backtest for a specific algorithm and coin"""
        print(f"\n--- Running {algorithm_name} backtest for {coin} ---")
        
        # Initialize optimizer
        optimizer = ParameterOptimizer(algorithm_name, data, coin)
        
        # Run optimization
        start_time = time.time()
        best_result = optimizer.optimize()
        end_time = time.time()
        
        print(f"Optimization completed in {end_time - start_time:.2f} seconds")
        
        if best_result['parameters'] is None:
            print(f"❌ No valid results found for {algorithm_name} on {coin}")
            return None
        
        # Display results
        print(f"\n✅ Best {algorithm_name} strategy for {coin}:")
        print(f"Win Rate: {best_result['metrics']['win_rate']:.2f}%")
        print(f"Total Trades: {best_result['metrics']['total_trades']}")
        print(f"Total Profit: {best_result['metrics']['total_profit']:.2f}%")
        print(f"Profit Factor: {best_result['metrics']['profit_factor']:.2f}")
        print(f"Parameters: {best_result['parameters']}")
        
        return best_result
    
    def plot_backtest_results(self, algorithm_name: str, coin: str, data: pd.DataFrame, 
                             trades_df: pd.DataFrame, metrics: Dict):
        """Create and save backtest visualization plots
        
        Args:
            algorithm_name: Name of the algorithm
            coin: Coin symbol
            data: Price data DataFrame
            trades_df: DataFrame containing trade information
            metrics: Dictionary of performance metrics
        """
        if not settings.SAVE_PLOTS:
            return
        
        try:
            # Create plots directory if it doesn't exist
            plots_dir = os.path.join(settings.RESULTS_DIR, 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            
            # Get the actual parameters used for this backtest from the result
            # We need to pass the parameters to recreate the algorithm correctly
            try:
                # Get parameters from the save_results call - they're stored in self
                if hasattr(self, '_current_algorithm_params'):
                    algo_params = self._current_algorithm_params
                else:
                    # Fallback: try to extract from metrics (won't have all params)
                    algo_params = {}
                
                # Create algorithm instance with the actual parameters used
                algorithm = AlgorithmFactory.create_algorithm(algorithm_name, **algo_params)
                data_with_indicators = algorithm.calculate_indicators(data)
            except Exception as e:
                print(f"Warning: Could not calculate indicators: {e}")
                data_with_indicators = data
            
            # Create figure with subplots based on algorithm type
            if 'RSI' in algorithm_name or 'STOCHASTIC' in algorithm_name:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                              gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=(16, 8))
                ax2 = None
            
            fig.suptitle(f'{algorithm_name} Backtest Results - {coin}', fontsize=16, fontweight='bold')
            
            # Plot 1: Price chart with buy/sell signals
            ax1.plot(data.index, data['price'], label='Price', color='blue', linewidth=1.5)
            
            # Add entry and exit signals
            if not trades_df.empty:
                # Plot entry points
                ax1.scatter(trades_df['entry_time'], trades_df['entry_price'], 
                          color='green', marker='^', s=150, label='Entry (Buy)', zorder=5, edgecolors='darkgreen', linewidths=1.5)
                
                # Plot exit points
                ax1.scatter(trades_df['exit_time'], trades_df['exit_price'], 
                          color='red', marker='v', s=150, label='Exit (Sell)', zorder=5, edgecolors='darkred', linewidths=1.5)
            
            ax1.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3)
            ax1.set_title('Price Chart with Trade Signals', fontsize=13, fontweight='bold')
            
            # Plot 2: Indicator (RSI, Stochastic, etc.)
            if ax2 is not None:
                if 'RSI' in algorithm_name and 'rsi' in data_with_indicators.columns:
                    ax2.plot(data_with_indicators.index, data_with_indicators['rsi'], 
                            label='RSI', color='purple', linewidth=1.5)
                    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
                    ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
                    ax2.fill_between(data_with_indicators.index, 30, 70, alpha=0.1, color='gray')
                    ax2.set_ylabel('RSI', fontsize=12, fontweight='bold')
                    ax2.set_ylim(0, 100)
                    ax2.legend(loc='upper left', fontsize=9)
                    ax2.grid(True, alpha=0.3)
                    ax2.set_title('RSI Indicator', fontsize=11, fontweight='bold')
                    
                    # Mark entry points on RSI
                    if not trades_df.empty:
                        for _, trade in trades_df.iterrows():
                            entry_idx = data_with_indicators.index.get_indexer([trade['entry_time']], method='nearest')[0]
                            if entry_idx < len(data_with_indicators):
                                rsi_val = data_with_indicators['rsi'].iloc[entry_idx]
                                ax2.scatter(trade['entry_time'], rsi_val, color='green', marker='o', s=80, zorder=5, edgecolors='darkgreen')
                
                elif 'STOCHASTIC' in algorithm_name and 'stoch_k' in data_with_indicators.columns:
                    ax2.plot(data_with_indicators.index, data_with_indicators['stoch_k'], 
                            label='%K', color='blue', linewidth=1.5)
                    ax2.plot(data_with_indicators.index, data_with_indicators['stoch_d'], 
                            label='%D', color='red', linewidth=1.5)
                    ax2.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Overbought (80)')
                    ax2.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='Oversold (20)')
                    ax2.fill_between(data_with_indicators.index, 20, 80, alpha=0.1, color='gray')
                    ax2.set_ylabel('Stochastic', fontsize=12, fontweight='bold')
                    ax2.set_ylim(0, 100)
                    ax2.legend(loc='upper left', fontsize=9)
                    ax2.grid(True, alpha=0.3)
                    ax2.set_title('Stochastic Oscillator', fontsize=11, fontweight='bold')
                
                ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            else:
                ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            
            plt.xticks(rotation=45)
            
            # Add metrics text box
            metrics_text = (
                f"Trades: {metrics['total_trades']} | "
                f"Win Rate: {metrics['win_rate']:.1f}% | "
                f"Total Profit: {metrics['total_profit']:.2f}% | "
                f"Profit Factor: {metrics['profit_factor']:.2f}\n"
                f"Max Drawdown: {metrics['max_drawdown']:.2f}% | "
                f"Avg Profit/Trade: {metrics['avg_profit']:.2f}%"
            )
            
            props = dict(boxstyle='round', facecolor='lightblue', alpha=0.9, edgecolor='navy', linewidth=2)
            ax1.text(0.5, 0.98, metrics_text, transform=ax1.transAxes, 
                    fontsize=10, verticalalignment='top', horizontalalignment='center',
                    bbox=props, fontweight='bold')
            
            # Adjust layout and save
            plt.tight_layout()
            
            # Create filename with timestamp
            plot_filename = f"{algorithm_name}_{coin}_{self.run_timestamp}.png"
            plot_filepath = os.path.join(plots_dir, plot_filename)
            
            plt.savefig(plot_filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Plot saved to {plot_filepath}")
            
        except Exception as e:
            print(f"⚠️  Error creating plot: {e}")
            import traceback
            traceback.print_exc()
    
    def save_results(self, algorithm_name: str, coin: str, result: Dict):
        """Save backtest results to JSON file with timestamp"""
        if result is None:
            return
        
        # Use the run timestamp (created once per run)
        if self.results_filepath is None:
            filename = f"best_results_{self.run_timestamp}.json"
            self.results_filepath = os.path.join(settings.RESULTS_DIR, filename)
        
        # Load existing results from this run's file or create new structure
        if os.path.exists(self.results_filepath):
            with open(self.results_filepath, 'r') as f:
                all_results = json.load(f)
        else:
            all_results = {"strategies": []}
        
        # Convert numpy types to native Python types
        def convert_types(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(v) for v in obj]
            return obj
        
        # Prepare new result
        new_result = {
            'strategy_name': algorithm_name,
            'coin': coin,
            'timeframe': settings.TIMEFRAME,
            'optimization_date': datetime.now().isoformat(),
            'data_points': len(self.current_data) if hasattr(self, 'current_data') else 0,
            'parameters': convert_types(result['parameters']),
            'win_rate': float(result['metrics']['win_rate']),
            'metrics': convert_types(result['metrics'])
        }
        
        # Remove existing result for this algorithm and coin
        all_results["strategies"] = [
            r for r in all_results["strategies"] 
            if not (r.get('strategy_name') == algorithm_name and r.get('coin') == coin)
        ]
        
        # Add new result
        all_results["strategies"].append(new_result)
        
        # Sort by total profit
        all_results["strategies"].sort(key=lambda x: x['metrics']['total_profit'], reverse=True)
        
        # Save to file
        with open(self.results_filepath, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"Results saved to {self.results_filepath}")
        
        # Create plot if enabled
        if settings.SAVE_PLOTS and result.get('trades_df') is not None:
            # Store the algorithm parameters so plot can use them
            algo_params = {k: v for k, v in result['parameters'].items() 
                          if k not in ['take_profit', 'stop_loss']}
            self._current_algorithm_params = algo_params
            
            self.plot_backtest_results(
                algorithm_name=algorithm_name,
                coin=coin,
                data=self.current_data,
                trades_df=result['trades_df'],
                metrics=result['metrics']
            )
    
    def _get_latest_results_file(self) -> Optional[str]:
        """Get the path to the latest results file"""
        try:
            # Get all result files
            result_files = [
                f for f in os.listdir(settings.RESULTS_DIR)
                if f.startswith("best_results_") and f.endswith(".json")
            ]
            
            if not result_files:
                return None
            
            # Sort by filename (timestamp is in filename)
            result_files.sort(reverse=True)
            
            return os.path.join(settings.RESULTS_DIR, result_files[0])
        except Exception as e:
            print(f"Error getting latest results file: {e}")
            return None
    
    def _cleanup_old_results(self):
        """Keep only the latest 5 result files"""
        try:
            # Get all result files
            result_files = [
                f for f in os.listdir(settings.RESULTS_DIR)
                if f.startswith("best_results_") and f.endswith(".json")
            ]
            
            if len(result_files) <= 5:
                return
            
            # Sort by filename (timestamp is in filename) - newest first
            result_files.sort(reverse=True)
            
            # Delete files beyond the 5 most recent
            for old_file in result_files[5:]:
                old_filepath = os.path.join(settings.RESULTS_DIR, old_file)
                os.remove(old_filepath)
                print(f"Removed old results file: {old_file}")
                
        except Exception as e:
            print(f"Error cleaning up old results: {e}")
    
    def display_final_summary(self):
        """Display final summary of all results from latest file"""
        filepath = self._get_latest_results_file()
        
        if not filepath or not os.path.exists(filepath):
            print("No results file found")
            return
        
        print(f"\nReading results from: {os.path.basename(filepath)}")
        
        with open(filepath, 'r') as f:
            all_results = json.load(f)
        
        strategies = all_results.get("strategies", [])
        
        if not strategies:
            print("No strategies found in results")
            return
        
        print("\n" + "="*80)
        print("FINAL BACKTESTING SUMMARY - BEST STRATEGIES")
        print("="*80)
        
        # Find best strategy overall
        best_strategy = strategies[0]  # Already sorted by total profit
        
        print(f"\n🏆 BEST OVERALL STRATEGY:")
        print(f"Algorithm: {best_strategy['strategy_name']}")
        print(f"Coin: {best_strategy['coin']}")
        print(f"Win Rate: {best_strategy['win_rate']:.2f}%")
        print(f"Total Trades: {best_strategy['metrics']['total_trades']}")
        print(f"Total Profit: {best_strategy['metrics']['total_profit']:.2f}%")
        print(f"Profit Factor: {best_strategy['metrics']['profit_factor']:.2f}")
        print(f"Parameters: {best_strategy['parameters']}")
        
        print(f"\n📊 ALL STRATEGIES RANKED BY TOTAL PROFIT:")
        print("-" * 80)
        
        for i, strategy in enumerate(strategies[:10], 1):  # Show top 10
            print(f"{i:2d}. {strategy['strategy_name']:4s} | {strategy['coin']:3s} | "
                  f"Win Rate: {strategy['win_rate']:6.2f}% | "
                  f"Trades: {strategy['metrics']['total_trades']:3d} | "
                  f"Profit: {strategy['metrics']['total_profit']:7.2f}%")
    
    def run(self, selected_algorithms: Optional[List[str]] = None):
        """Run the complete backtesting system
        
        Args:
            selected_algorithms: List of algorithm names to run. If None, runs all algorithms.
        """
        # Use selected algorithms or default to all
        algorithms_to_run = selected_algorithms if selected_algorithms is not None else settings.ALGORITHMS
        
        print("="*80)
        print("MULTI-ALGORITHM CRYPTO BACKTESTING SYSTEM")
        print("="*80)
        print(f"Coins: {', '.join(settings.COINS)}")
        print(f"Algorithms: {', '.join(algorithms_to_run)}")
        
        # Show timeframe info
        has_4h_algos = any(algo in ["RSI_4H", "RSI_4H_DOUBLE_CONFIRM"] for algo in algorithms_to_run)
        has_5m_algos = any(algo == "RSI_5MIN_DOUBLE_CONFIRM" for algo in algorithms_to_run)
        has_1m_algos = any(algo not in ["RSI_4H", "RSI_4H_DOUBLE_CONFIRM", "RSI_5MIN_DOUBLE_CONFIRM"] for algo in algorithms_to_run)
        
        timeframes = []
        if has_1m_algos:
            timeframes.append("1-minute")
        if has_5m_algos:
            timeframes.append("5-minute")
        if has_4h_algos:
            timeframes.append("4-hour")
        
        if len(timeframes) > 1:
            print(f"Timeframes: {' + '.join(timeframes)}")
        elif timeframes:
            print(f"Timeframe: {timeframes[0]}")
        else:
            print(f"Timeframe: {settings.TIMEFRAME}")
        
        # Step 1: Download historical data
        if not self.download_historical_data():
            print("❌ Failed to download data. Exiting.")
            return
        
        # Step 2: Run backtests for each coin and algorithm
        for coin in settings.COINS:
            print(f"\n{'='*60}")
            print(f"PROCESSING {coin}")
            print(f"{'='*60}")
            
            # Run each selected algorithm
            for algorithm_name in algorithms_to_run:
                try:
                    # Load data for this coin and algorithm (RSI_4H uses different timeframe)
                    data = self.load_data(coin, algorithm_name)
                    if data is None:
                        print(f"❌ Skipping {algorithm_name} on {coin} - no data available")
                        continue
                    
                    self.current_data = data  # Store for saving results
                    
                    result = self.run_algorithm_backtest(algorithm_name, coin, data)
                    if result:
                        self.save_results(algorithm_name, coin, result)
                        self.results.append({
                            'algorithm': algorithm_name,
                            'coin': coin,
                            'result': result
                        })
                except Exception as e:
                    print(f"❌ Error running {algorithm_name} on {coin}: {e}")
                    continue
        
        # Step 3: Clean up old result files and display final summary
        self._cleanup_old_results()
        self.display_final_summary()
        
        print(f"\n✅ Backtesting completed! Check {settings.RESULTS_DIR}/ for detailed results.")


def display_algorithm_menu() -> List[str]:
    """Display algorithm selection menu and return selected algorithms"""
    print("\n" + "="*80)
    print("ALGORITHM SELECTION")
    print("="*80)
    print("\nAvailable algorithms:")
    print("  0. Run ALL algorithms")
    
    for i, algo in enumerate(settings.ALGORITHMS, 1):
        print(f"  {i}. {algo}")
    
    print("\nEnter your choice (0 for all, or 1-{} for specific algorithm): ".format(len(settings.ALGORITHMS)), end='')
    
    try:
        choice = input().strip()
        
        if not choice.isdigit():
            print("❌ Invalid input. Running all algorithms by default.")
            return settings.ALGORITHMS
        
        choice_num = int(choice)
        
        if choice_num == 0:
            print("✅ Running ALL algorithms")
            return settings.ALGORITHMS
        elif 1 <= choice_num <= len(settings.ALGORITHMS):
            selected_algo = settings.ALGORITHMS[choice_num - 1]
            print(f"✅ Running only: {selected_algo}")
            return [selected_algo]
        else:
            print(f"❌ Invalid choice. Please enter 0-{len(settings.ALGORITHMS)}. Running all algorithms by default.")
            return settings.ALGORITHMS
            
    except Exception as e:
        print(f"❌ Error reading input: {e}. Running all algorithms by default.")
        return settings.ALGORITHMS


def main():
    """Main entry point"""
    try:
        # Display algorithm selection menu
        selected_algorithms = display_algorithm_menu()
        
        # Create system and run with selected algorithms
        system = BacktestingSystem()
        system.run(selected_algorithms=selected_algorithms)
    except KeyboardInterrupt:
        print("\n❌ Backtesting interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
