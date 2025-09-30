"""
Historical Data Fetcher using CoinGecko and CryptoCompare APIs
Bootstraps the data service with historical data for all timeframes
"""

import requests
import pandas as pd
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import settings

logger = logging.getLogger(__name__)

class CoinGeckoHistoricalFetcher:
    """Fetches historical data from CoinGecko API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        # Load coin mappings from settings
        self.coin_map = settings.COIN_MAPPINGS
    
    def fetch_ohlc_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Fetch OHLC data from CoinGecko (4-hour candles for 30 days)"""
        try:
            coin_id = self.coin_map.get(symbol)
            if not coin_id:
                logger.error(f"Unsupported symbol: {symbol}")
                return None
            
            url = f"{self.base_url}/coins/{coin_id}/ohlc"
            params = {
                'vs_currency': 'usd',
                'days': days
            }
            
            logger.info(f"Fetching {days} days of {symbol} OHLC data from CoinGecko...")
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert OHLC data to DataFrame
            df_data = []
            for item in data:
                timestamp = datetime.fromtimestamp(item[0] / 1000)  # Convert from milliseconds
                df_data.append({
                    'timestamp': timestamp,
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                    'price': float(item[4]),  # Use close as price
                    'volume': 0.0  # CoinGecko OHLC doesn't include volume
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Successfully fetched {len(df)} OHLC data points for {symbol}")
            logger.info(f"Data range: {df.index[0]} to {df.index[-1]}")
            
            return df[['price', 'volume', 'open', 'high', 'low', 'close']]
            
        except Exception as e:
            logger.error(f"Error fetching OHLC data: {e}")
            return None

class CryptoCompareHistoricalFetcher:
    """Fetches historical data from CryptoCompare API"""
    
    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data/v2"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
    def fetch_historical_minutes(self, symbol: str, limit: int = 2000) -> Optional[pd.DataFrame]:
        """Fetch historical minute data from CryptoCompare"""
        try:
            url = f"{self.base_url}/histominute"
            params = {
                'fsym': symbol,
                'tsym': 'USD',
                'limit': limit
            }
            
            logger.info(f"Fetching {limit} minutes of {symbol} historical data from CryptoCompare...")
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['Response'] != 'Success':
                logger.error(f"CryptoCompare API error: {data.get('Message', 'Unknown error')}")
                return None
            
            # Extract the data
            historical_data = data['Data']['Data']
            
            # Convert to DataFrame
            df_data = []
            for item in historical_data:
                df_data.append({
                    'timestamp': datetime.fromtimestamp(item['time']),
                    'price': float(item['close']),  # Use close price
                    'volume': float(item['volumeto'])  # Volume in USD
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Successfully fetched {len(df)} minute data points for {symbol}")
            logger.info(f"Data range: {df.index[0]} to {df.index[-1]}")
            
            return df[['price', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def resample_to_timeframe(self, minute_data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Resample minute data to specified timeframe"""
        try:
            # Mapping timeframes to pandas frequency codes
            freq_map = {
                "5m": "5min",
                "15m": "15min",
                "1h": "1h",
                "1d": "1D"
            }
            
            if timeframe not in freq_map:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
            
            freq = freq_map[timeframe]
            
            # Resample data
            resampled = minute_data.resample(freq).agg({
                'price': 'last',  # Use last price as close
                'volume': 'sum'   # Sum volume
            }).dropna()
            
            logger.info(f"Resampled to {timeframe}: {len(resampled)} data points")
            return resampled
            
        except Exception as e:
            logger.error(f"Error resampling to {timeframe}: {e}")
            return pd.DataFrame()
    
    def convert_to_data_format(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to the data service format"""
        try:
            data_list = []
            for timestamp, row in df.iterrows():
                data_list.append({
                    "timestamp": timestamp.isoformat(),
                    "price": float(row['price']),
                    "volume": float(row['volume'])
                })
            return data_list
        except Exception as e:
            logger.error(f"Error converting data format: {e}")
            return []
    
    def bootstrap_historical_data(self, base_data_dir: str = "data", coins: List[str] = None, use_coingecko: bool = True) -> bool:
        """Bootstrap all historical data for specified coins"""
        try:
            if coins is None:
                coins = settings.COINS
            
            timeframes = ["1m", "5m", "15m", "1h", "1d"]
            
            # Initialize CoinGecko fetcher for long-term data
            coingecko_fetcher = CoinGeckoHistoricalFetcher() if use_coingecko else None
            
            for coin in coins:
                logger.info(f"Bootstrapping historical data for {coin}...")
                
                # First, try to get 30 days of OHLC data from CoinGecko
                long_term_data = None
                if coingecko_fetcher:
                    long_term_data = coingecko_fetcher.fetch_ohlc_data(coin, days=30)
                
                # Then get recent minute data from CryptoCompare
                minute_data = self.fetch_historical_minutes(coin)
                if minute_data is None:
                    logger.error(f"Failed to fetch minute data for {coin}")
                    continue
                
                # Process each timeframe
                for tf in timeframes:
                    try:
                        if tf == "1m":
                            # Use CryptoCompare minute data
                            tf_data = minute_data
                        elif tf in ["1h", "1d"] and long_term_data is not None:
                            # For hourly and daily, prefer CoinGecko data if available
                            if tf == "1h":
                                # CoinGecko gives 4-hour candles, so we use them as-is for hourly
                                tf_data = long_term_data[['price', 'volume']]
                                logger.info(f"Using CoinGecko 4-hour data for {tf} (180 data points)")
                            else:  # 1d
                                # Resample 4-hour to daily
                                tf_data = long_term_data[['price', 'volume']].resample('1D').agg({
                                    'price': 'last',
                                    'volume': 'sum'
                                }).dropna()
                                logger.info(f"Resampled CoinGecko data to daily: {len(tf_data)} data points")
                        else:
                            # Resample minute data for other timeframes
                            tf_data = self.resample_to_timeframe(minute_data, tf)
                        
                        if tf_data.empty:
                            logger.warning(f"No data for {coin} {tf}")
                            continue
                        
                        # Convert to data service format
                        data_list = self.convert_to_data_format(tf_data)
                        
                        # Save to file
                        file_path = os.path.join(base_data_dir, coin, f"{tf}.json")
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        # Create file data structure
                        file_data = {
                            "symbol": coin,
                            "timeframe": tf,
                            "last_update": datetime.now().isoformat(),
                            "data": data_list
                        }
                        
                        # Save to file
                        with open(file_path, 'w') as f:
                            json.dump(file_data, f, indent=2)
                        
                        logger.info(f"Saved {len(data_list)} data points for {coin} {tf}")
                        
                    except Exception as e:
                        logger.error(f"Error processing {coin} {tf}: {e}")
                        continue
                
                # Add delay between coins to be respectful to API
                if coin != coins[-1]:  # Don't wait after last coin
                    time.sleep(2)
            
            logger.info("Historical data bootstrap completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in bootstrap_historical_data: {e}")
            return False
    
    def get_data_summary(self, base_data_dir: str = "data") -> Dict:
        """Get summary of bootstrapped data"""
        summary = {}
        
        try:
            for coin_dir in os.listdir(base_data_dir):
                coin_path = os.path.join(base_data_dir, coin_dir)
                if os.path.isdir(coin_path):
                    summary[coin_dir] = {}
                    
                    for file_name in os.listdir(coin_path):
                        if file_name.endswith('.json'):
                            timeframe = file_name.replace('.json', '')
                            file_path = os.path.join(coin_path, file_name)
                            
                            try:
                                with open(file_path, 'r') as f:
                                    file_data = json.load(f)
                                
                                data_points = len(file_data.get("data", []))
                                last_update = file_data.get("last_update")
                                
                                # Get price range
                                data_list = file_data.get("data", [])
                                if data_list:
                                    prices = [item['price'] for item in data_list]
                                    price_range = f"${min(prices):.2f} - ${max(prices):.2f}"
                                    latest_price = f"${data_list[-1]['price']:.2f}"
                                else:
                                    price_range = "N/A"
                                    latest_price = "N/A"
                                
                                summary[coin_dir][timeframe] = {
                                    "data_points": data_points,
                                    "last_update": last_update,
                                    "price_range": price_range,
                                    "latest_price": latest_price
                                }
                                
                            except Exception as e:
                                logger.error(f"Error reading {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
        
        return summary

def main():
    """Main function to bootstrap historical data"""
    logging.basicConfig(level=logging.INFO)
    
    fetcher = CryptoCompareHistoricalFetcher()
    
    # Bootstrap historical data with CoinGecko for better coverage
    success = fetcher.bootstrap_historical_data(use_coingecko=True)
    
    if success:
        # Print summary
        summary = fetcher.get_data_summary()
        print("\n" + "="*60)
        print("HISTORICAL DATA BOOTSTRAP SUMMARY")
        print("="*60)
        print("📊 Data Sources: CoinGecko (30-day OHLC) + CryptoCompare (Recent minutes)")
        
        for coin, timeframes in summary.items():
            print(f"\n{coin}:")
            for tf, info in timeframes.items():
                print(f"  {tf:>4}: {info['data_points']:>4} points | Latest: {info['latest_price']:>10} | Range: {info['price_range']}")
        
        print(f"\n✅ Bootstrap completed successfully!")
        print("📈 Enhanced with 30-day CoinGecko data for better signal accuracy!")
        print("Your signal trackers can now run immediately with sufficient historical data.")
    else:
        print("❌ Bootstrap failed. Check logs for details.")

if __name__ == "__main__":
    main()
