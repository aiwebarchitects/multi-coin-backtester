#!/usr/bin/env python3
"""
Simplified Bitcoin 1-minute data fetcher using Binance API
Fetches 24 hours of BTC/USDT 1-minute kline data
"""

import requests
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceBTCFetcher:
    """Fetches 1-minute Bitcoin data from Binance API"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.symbol = "BTCUSDT"
        self.interval = "1m"
        self.limit = 1440  # 24 hours * 60 minutes = 1440 data points
    
    def fetch_klines(self) -> Optional[List[Dict]]:
        """Fetch 1-minute klines for the last 24 hours"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': self.symbol,
                'interval': self.interval,
                'limit': self.limit
            }
            
            logger.info(f"Fetching {self.limit} minutes of {self.symbol} data from Binance...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            klines = response.json()
            
            # Convert klines to our format
            data_list = []
            for kline in klines:
                timestamp = datetime.fromtimestamp(int(kline[0]) / 1000)  # Convert from milliseconds
                
                data_point = {
                    "timestamp": timestamp.isoformat(),
                    "price": float(kline[4]),  # Close price
                    "volume": float(kline[5]),  # Volume
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4])
                }
                data_list.append(data_point)
            
            logger.info(f"Successfully fetched {len(data_list)} data points")
            if data_list:
                logger.info(f"Data range: {data_list[0]['timestamp']} to {data_list[-1]['timestamp']}")
                logger.info(f"Latest BTC price: ${data_list[-1]['price']:,.2f}")
            
            return data_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            return None
    
    def save_data(self, data: List[Dict], filename: str = "btc_1m_24h.json") -> bool:
        """Save data to JSON file"""
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            file_path = os.path.join("data", filename)
            
            # Create file data structure
            file_data = {
                "symbol": "BTC",
                "exchange": "Binance",
                "timeframe": "1m",
                "period": "24h",
                "data_points": len(data),
                "last_update": datetime.now().isoformat(),
                "data": data
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            logger.info(f"Data saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def get_data_summary(self, data: List[Dict]) -> Dict:
        """Get summary of the fetched data"""
        if not data:
            return {}
        
        prices = [item['price'] for item in data]
        volumes = [item['volume'] for item in data]
        
        return {
            "symbol": "BTC/USDT",
            "exchange": "Binance",
            "timeframe": "1 minute",
            "period": "24 hours",
            "data_points": len(data),
            "price_range": {
                "min": f"${min(prices):,.2f}",
                "max": f"${max(prices):,.2f}",
                "latest": f"${prices[-1]:,.2f}"
            },
            "volume_total": f"{sum(volumes):,.2f} BTC",
            "time_range": {
                "start": data[0]['timestamp'],
                "end": data[-1]['timestamp']
            }
        }

def main():
    """Main function to fetch and save Bitcoin data"""
    print("🚀 Bitcoin 1-Minute Data Fetcher (24h from Binance)")
    print("=" * 50)
    
    fetcher = BinanceBTCFetcher()
    
    # Fetch data
    data = fetcher.fetch_klines()
    
    if data:
        # Save data
        success = fetcher.save_data(data)
        
        if success:
            # Print summary
            summary = fetcher.get_data_summary(data)
            
            print("\n📊 DATA SUMMARY")
            print("-" * 30)
            print(f"Symbol: {summary['symbol']}")
            print(f"Exchange: {summary['exchange']}")
            print(f"Timeframe: {summary['timeframe']}")
            print(f"Period: {summary['period']}")
            print(f"Data points: {summary['data_points']}")
            print(f"Latest price: {summary['price_range']['latest']}")
            print(f"24h range: {summary['price_range']['min']} - {summary['price_range']['max']}")
            print(f"Total volume: {summary['volume_total']}")
            print(f"\n✅ Data successfully saved to 'data/btc_1m_24h.json'")
        else:
            print("❌ Failed to save data")
    else:
        print("❌ Failed to fetch data from Binance")

if __name__ == "__main__":
    main()
