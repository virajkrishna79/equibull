import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.upstox_api_key = os.getenv('UPSTOX_API_KEY')
        self.upstox_base_url = 'https://api.upstox.com/v2'
        self.fallback_to_yahoo = True
        
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock data for a given symbol
        Tries Upstox first, falls back to Yahoo Finance
        """
        try:
            # Try Upstox API first
            if self.upstox_api_key:
                data = self._get_upstox_data(symbol)
                if data:
                    return data
            
            # Fallback to Yahoo Finance
            if self.fallback_to_yahoo:
                return self._get_yahoo_data(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            
        return self._get_default_data(symbol)
    
    def _get_upstox_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Upstox API"""
        try:
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.upstox_api_key}'
            }
            
            # Get market quote
            url = f"{self.upstox_base_url}/market-quote/ltp"
            params = {'symbol': symbol}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response
            if 'data' in data and data['data']:
                quote_data = data['data'][0]
                return {
                    'symbol': symbol,
                    'current_price': quote_data.get('ltp', 0),
                    'change': quote_data.get('change', 0),
                    'change_percent': quote_data.get('change_percent', 0),
                    'volume': quote_data.get('volume', 0),
                    'high': quote_data.get('high', 0),
                    'low': quote_data.get('low', 0),
                    'open': quote_data.get('open', 0),
                    'previous_close': quote_data.get('previous_close', 0),
                    'source': 'upstox'
                }
                
        except Exception as e:
            logger.warning(f"Upstox API failed for {symbol}: {e}")
            
        return None
    
    def _get_yahoo_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from Yahoo Finance as fallback"""
        try:
            # Add .NS suffix for Indian stocks if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            hist = ticker.history(period="5d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            return {
                'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                'current_price': current_price,
                'change': hist['Close'].iloc[-1] - hist['Close'].iloc[-2] if len(hist) > 1 else 0,
                'change_percent': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0,
                'volume': hist['Volume'].iloc[-1] if not hist.empty else 0,
                'high': hist['High'].iloc[-1] if not hist.empty else 0,
                'low': hist['Low'].iloc[-1] if not hist.empty else 0,
                'open': hist['Open'].iloc[-1] if not hist.empty else 0,
                'previous_close': hist['Close'].iloc[-2] if len(hist) > 1 else 0,
                'source': 'yahoo_finance'
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance failed for {symbol}: {e}")
            return self._get_default_data(symbol)
    
    def _get_default_data(self, symbol: str) -> Dict[str, Any]:
        """Return default data structure when APIs fail"""
        return {
            'symbol': symbol,
            'current_price': 0,
            'change': 0,
            'change_percent': 0,
            'volume': 0,
            'high': 0,
            'low': 0,
            'open': 0,
            'previous_close': 0,
            'source': 'default'
        }
    
    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for technical analysis"""
        try:
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Calculate technical indicators for a stock"""
        try:
            hist_data = self.get_historical_data(symbol, days=50)
            if hist_data.empty:
                return {}
            
            # Calculate RSI
            delta = hist_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Calculate Moving Averages
            sma_20 = hist_data['Close'].rolling(window=20).mean()
            sma_50 = hist_data['Close'].rolling(window=50).mean()
            
            # Calculate MACD
            ema_12 = hist_data['Close'].ewm(span=12).mean()
            ema_26 = hist_data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            return {
                'rsi': rsi.iloc[-1] if not rsi.empty else 0,
                'sma_20': sma_20.iloc[-1] if not sma_20.empty else 0,
                'sma_50': sma_50.iloc[-1] if not sma_50.empty else 0,
                'macd': macd.iloc[-1] if not macd.empty else 0,
                'macd_signal': signal.iloc[-1] if not signal.empty else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return {}
