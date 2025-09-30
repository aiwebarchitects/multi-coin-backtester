#!/usr/bin/env python3
"""
Simple RSI Backtest Algorithm
RSI below 30 = BUY signal
RSI above 70 = SELL signal
Uses 24h Bitcoin 1-minute data from Binance
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class RSIBacktest:
    def __init__(self, data_file: str = "data/btc_1m_24h.json"):
        self.data_file = data_file
        self.rsi_period = 14
        self.oversold_threshold = 30
        self.overbought_threshold = 70
        self.initial_balance = 10000  # $10,000 starting capital
        
    def load_data(self) -> pd.DataFrame:
        """Load Bitcoin data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                file_data = json.load(f)
            
            data = file_data['data']
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            
            print(f"✅ Loaded {len(df)} data points")
            print(f"📅 Data range: {df.index[0]} to {df.index[-1]}")
            print(f"💰 Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on RSI"""
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)
        
        # Generate signals
        df['signal'] = 0  # 0 = hold, 1 = buy, -1 = sell
        
        # Buy when RSI < 30 (oversold)
        df.loc[df['rsi'] < self.oversold_threshold, 'signal'] = 1
        
        # Sell when RSI > 70 (overbought) 
        df.loc[df['rsi'] > self.overbought_threshold, 'signal'] = -1
        
        # Create position column (1 = long, 0 = no position)
        df['position'] = 0
        
        return df
    
    def backtest_strategy(self, df: pd.DataFrame) -> Dict:
        """Run the backtest simulation"""
        balance = self.initial_balance
        position = 0  # 0 = no position, > 0 = number of BTC held
        trades = []
        equity_curve = []
        
        buy_price = 0
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['price']
            signal = row['signal']
            rsi = row['rsi']
            
            # Skip if RSI not calculated yet
            if pd.isna(rsi):
                equity_curve.append(balance)
                continue
            
            # Execute trades
            if signal == 1 and position == 0:  # Buy signal and no current position
                position = balance / current_price  # Buy maximum possible
                buy_price = current_price
                balance = 0  # All cash invested
                
                trades.append({
                    'timestamp': timestamp,
                    'action': 'BUY',
                    'price': current_price,
                    'rsi': rsi,
                    'amount': position
                })
                
            elif signal == -1 and position > 0:  # Sell signal and holding position
                balance = position * current_price  # Sell all
                
                # Calculate trade return
                trade_return = ((current_price - buy_price) / buy_price) * 100
                
                trades.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': current_price,
                    'rsi': rsi,
                    'amount': position,
                    'return_pct': trade_return
                })
                
                position = 0
            
            # Calculate current equity
            current_equity = balance + (position * current_price if position > 0 else 0)
            equity_curve.append(current_equity)
        
        # Final equity calculation
        final_price = df['price'].iloc[-1]
        final_equity = balance + (position * final_price if position > 0 else 0)
        
        return {
            'trades': trades,
            'equity_curve': equity_curve,
            'final_equity': final_equity,
            'total_return_pct': ((final_equity - self.initial_balance) / self.initial_balance) * 100,
            'final_position': position,
            'final_price': final_price
        }
    
    def analyze_results(self, results: Dict) -> None:
        """Print backtest results analysis"""
        trades = results['trades']
        final_equity = results['final_equity']
        total_return = results['total_return_pct']
        
        # Separate buy and sell trades
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        
        print("\n" + "="*60)
        print("🚀 RSI BACKTEST RESULTS")
        print("="*60)
        print(f"📈 Strategy: RSI({self.rsi_period}) - Buy<{self.oversold_threshold}, Sell>{self.overbought_threshold}")
        print(f"💰 Initial Capital: ${self.initial_balance:,.2f}")
        print(f"💰 Final Equity: ${final_equity:,.2f}")
        print(f"📊 Total Return: {total_return:+.2f}%")
        print(f"📈 Total Trades: {len(trades)} ({len(buy_trades)} buys, {len(sell_trades)} sells)")
        
        if sell_trades:
            returns = [t['return_pct'] for t in sell_trades]
            winning_trades = [r for r in returns if r > 0]
            losing_trades = [r for r in returns if r < 0]
            
            print(f"✅ Winning Trades: {len(winning_trades)}/{len(returns)} ({len(winning_trades)/len(returns)*100:.1f}%)")
            print(f"🎯 Average Win: {np.mean(winning_trades):.2f}%" if winning_trades else "🎯 Average Win: 0.00%")
            print(f"💸 Average Loss: {np.mean(losing_trades):.2f}%" if losing_trades else "💸 Average Loss: 0.00%")
            print(f"📈 Best Trade: {max(returns):.2f}%")
            print(f"📉 Worst Trade: {min(returns):.2f}%")
        
        # Show recent trades
        if trades:
            print(f"\n📋 RECENT TRADES:")
            print("-" * 60)
            for trade in trades[-5:]:  # Last 5 trades
                action = trade['action']
                price = trade['price']
                rsi = trade['rsi']
                timestamp = trade['timestamp']
                
                if action == 'SELL':
                    return_str = f" (Return: {trade['return_pct']:+.2f}%)"
                else:
                    return_str = ""
                
                print(f"{timestamp.strftime('%H:%M')} | {action:4} | ${price:8.2f} | RSI: {rsi:5.1f}{return_str}")
        
        # Current position status
        if results['final_position'] > 0:
            print(f"\n🔄 Current Position: {results['final_position']:.6f} BTC (${results['final_position'] * results['final_price']:,.2f})")
        else:
            print(f"\n💰 Current Position: CASH (${final_equity:,.2f})")

def main():
    """Main function to run RSI backtest"""
    print("🤖 Simple RSI Backtest Algorithm")
    print("📊 Strategy: Buy RSI<30, Sell RSI>70")
    print("⏱️  Data: Bitcoin 1-minute (24h)")
    print("-" * 50)
    
    # Initialize backtest
    backtest = RSIBacktest()
    
    # Load data
    df = backtest.load_data()
    if df.empty:
        print("❌ No data available. Run the data fetcher first!")
        return
    
    # Generate signals
    df = backtest.generate_signals(df)
    
    # Run backtest
    results = backtest.backtest_strategy(df)
    
    # Analyze results
    backtest.analyze_results(results)
    
    print(f"\n🎯 Backtest completed on {len(df)} data points!")

if __name__ == "__main__":
    main()
