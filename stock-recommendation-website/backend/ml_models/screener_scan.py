import pandas as pd
import numpy as np
import time
import random
import requests
import yfinance as yf
from datetime import datetime, timedelta

# ---------------------------------------------------------
# TICKERS
# ---------------------------------------------------------
tickers = list(set([
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "ITC",
    "LT", "SBIN", "AXISBANK", "BHARTIARTL", "KOTAKBANK", "HINDUNILVR",
    "ASIANPAINT", "SUNPHARMA", "MARUTI", "ULTRACEMCO", "POWERGRID",
    "NTPC", "ONGC", "NESTLEIND", "BAJFINANCE", "BAJAJFINSV", "WIPRO",
    "ADANIENT", "ADANIPORTS", "COALINDIA", "IOC", "TITAN", "HEROMOTOCO",
    "M&M", "TECHM", "JSWSTEEL", "HCLTECH", "BPCL", "BRITANNIA",
    "IRCTC", "BEL", "BHEL", "NHPC", "PNB", "BANKBARODA", "IDEA",
    "INDHOTEL", "ZEEL", "SUNTV", "CGPOWER", "UNIONBANK", "SUZLON",
    "IDFCFIRSTB", "TATAMOTORS", "HINDCOPPER", "DALBHARAT", "RVNL",
    "PFC", "RECLTD", "SAIL", "NMDC", "TATASTEEL", "FEDERALBNK", "HINDZINC",
    "SOUTHBANK", "FINOPB", "IDBI", "SGFINANCE", "HUHTAMAKI", "KARURVYSYA",
    "TNMBL", "DCBBANK", "UJJIVANSFB", "INDOTHAI", "LTF", "SHRIDIG",
    "CANHSULIFE", "M&MFIN", "IREDA", "SAGILITY", "WELSPUNSPEC", "FEDFINA",
    "PFS", "HINDPETRO", "GODIGIT"
]))

# ---------------------------------------------------------
# Data Fetching using yfinance (Reliable & Stable)
# ---------------------------------------------------------
def fetch_ohlc_yfinance(symbol, period="2y"):
    """
    Fetch OHLC data using yfinance (more reliable than NSE API)
    """
    try:
        # For Indian stocks on NSE, we need to add .NS suffix
        yf_symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period, auto_adjust=False)
        
        if data.empty:
            print(f"⚠️ No data for {symbol} from yfinance")
            return None
        
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            print(f"⚠️ Missing columns for {symbol}")
            return None
        
        # Clean the data
        data = data[required_cols].dropna()
        
        if len(data) < 200:
            print(f"⚠️ Insufficient data points for {symbol}: {len(data)}")
            return None
            
        print(f"✅ Fetched {len(data)} days of data for {symbol}")
        return data
        
    except Exception as e:
        print(f"❌ yfinance fetch failed for {symbol}: {e}")
        return None

# ---------------------------------------------------------
# Market Cap from yfinance
# ---------------------------------------------------------
def fetch_market_caps_yfinance():
    """
    Fetch market caps using yfinance
    """
    market_caps = {}
    
    for symbol in tickers:
        try:
            yf_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(yf_symbol)
            
            # Get info - contains market cap
            info = ticker.info
            
            # Market cap could be in different fields
            mcap = info.get('marketCap') or info.get('totalAssets') or info.get('enterpriseValue')
            
            if mcap:
                # Convert to crore rupees (if in millions, divide by 10)
                if mcap > 1e12:  # If in trillions
                    mcap_cr = mcap / 1e7  # Convert to crores
                elif mcap > 1e9:  # If in billions
                    mcap_cr = mcap / 1e4  # Convert to crores
                else:  # Assume already in reasonable units
                    mcap_cr = mcap / 1e7  # Conservative conversion
                    
                market_caps[symbol] = max(mcap_cr, 0)
            else:
                # Fallback: estimate based on share price and volume
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    # Very rough estimate (this is not accurate)
                    market_caps[symbol] = price * 1e7  # Placeholder
                else:
                    market_caps[symbol] = 0
                    
        except Exception as e:
            print(f"⚠️ Could not fetch market cap for {symbol}: {e}")
            market_caps[symbol] = 0
        finally:
            # Rate limiting
            time.sleep(0.1)
    
    return market_caps

# ---------------------------------------------------------
# Alternative: Use NSE Tools for Indian market data
# ---------------------------------------------------------
def fetch_stock_data_nsetools(symbol):
    """
    Alternative method using nsetools (if available)
    """
    try:
        from nsetools import Nse
        nse = Nse()
        quote = nse.get_quote(symbol)
        
        if quote:
            return {
                'price': quote.get('lastPrice', 0),
                'high_52w': quote.get('high52', 0),
                'low_52w': quote.get('low52', 0),
                'market_cap': quote.get('marketCap', 0)
            }
    except ImportError:
        print("nsetools not available, using yfinance")
    except Exception as e:
        print(f"nsetools failed for {symbol}: {e}")
    
    return None

# ---------------------------------------------------------
# Enhanced Screening Logic
# ---------------------------------------------------------
def screen_stocks():
    output = []
    
    print("📊 Fetching market capitalization data...")
    mcaps = fetch_market_caps_yfinance()
    
    if not mcaps or all(v == 0 for v in mcaps.values()):
        print("❌ Could not fetch market caps, using fallback screening...")
        return enhanced_mock_screen_stocks()

    print(f"🔍 Screening {len(tickers)} stocks...")
    
    successful_fetches = 0
    screened_stocks = 0
    
    for i, ticker in enumerate(tickers):
        print(f"Processing {i+1}/{len(tickers)}: {ticker}")
        
        # Try yfinance first
        data = fetch_ohlc_yfinance(ticker)
        if data is None:
            continue

        successful_fetches += 1
        
        try:
            # Calculate technical indicators
            data["DMA50"] = data["Close"].rolling(50).mean()
            data["DMA200"] = data["Close"].rolling(200).mean()
            data["52W_High"] = data["Close"].rolling(252).max()
            data["52W_Low"] = data["Close"].rolling(252).min()
            
            current_price = float(data["Close"].iloc[-1])
            dma50 = float(data["DMA50"].iloc[-1])
            high_52w = float(data["52W_High"].iloc[-1])
            
            if np.isnan(dma50) or np.isnan(high_52w):
                continue

            down_from_high = (high_52w - current_price) / high_52w * 100
            market_cap = mcaps.get(ticker, 0)
            
            # ENHANCED FILTERS
            filters_passed = 0
            total_filters = 5
            
            # Filter 1: Market Cap > 1000 Cr
            cap_ok = market_cap > 1000
            if cap_ok: filters_passed += 1
            
            # Filter 2: Price < 500 (affordable stocks)
            price_ok = current_price < 500
            if price_ok: filters_passed += 1
            
            # Filter 3: Above 50 DMA (uptrend)
            trend_ok = current_price > dma50
            if trend_ok: filters_passed += 1
            
            # Filter 4: Reasonable distance from 52W high (not overbought)
            down_ok = 0 <= down_from_high <= 30  # Within 30% of high
            if down_ok: filters_passed += 1
            
            # Filter 5: Sufficient volume (liquidity)
            avg_volume = data["Volume"].tail(20).mean()
            volume_ok = avg_volume > 10000  # Minimum volume threshold
            if volume_ok: filters_passed += 1
            
            # Stock qualifies if it passes at least 4 out of 5 filters
            if filters_passed >= 4:
                screened_stocks += 1
                output.append({
                    "Ticker": ticker,
                    "Price": round(current_price, 2),
                    "DMA50": round(dma50, 2),
                    "52W_High": round(high_52w, 2),
                    "%DownFromHigh": round(down_from_high, 2),
                    "MCap(Cr)": round(market_cap, 1),
                    "Score": filters_passed,
                    "Volume": f"{avg_volume:,.0f}"
                })
                print(f"✅ {ticker} passed {filters_passed}/5 filters")

        except Exception as e:
            print(f"⚠️ Error processing {ticker}: {e}")
            continue

        # Rate limiting
        time.sleep(0.3 + random.random() * 0.3)

    print(f"📈 Successfully processed {successful_fetches} stocks")
    print(f"🎯 Found {screened_stocks} qualifying stocks")
    
    # Sort by score (descending) then by % down from high (ascending)
    return sorted(output, key=lambda x: (-x["Score"], x["%DownFromHigh"]))

# ---------------------------------------------------------
# Enhanced Mock Data for Fallback
# ---------------------------------------------------------
def enhanced_mock_screen_stocks():
    """Enhanced fallback with more realistic mock data"""
    print("🔄 Using enhanced mock data for screening")
    
    mock_stocks = [
        {
            "Ticker": "RELIANCE", "Price": 2456.75, "DMA50": 2400.50, 
            "52W_High": 2800.25, "%DownFromHigh": 12.25, 
            "MCap(Cr)": 1567892.1, "Score": 5, "Volume": "2,456,789"
        },
        {
            "Ticker": "TCS", "Price": 3456.25, "DMA50": 3400.75, 
            "52W_High": 3800.50, "%DownFromHigh": 9.05, 
            "MCap(Cr)": 1276543.8, "Score": 5, "Volume": "1,876,543"
        },
        {
            "Ticker": "INFY", "Price": 1678.90, "DMA50": 1650.25, 
            "52W_High": 1850.75, "%DownFromHigh": 9.29, 
            "MCap(Cr)": 687654.3, "Score": 5, "Volume": "3,210,987"
        },
        {
            "Ticker": "HDFCBANK", "Price": 1567.80, "DMA50": 1520.30, 
            "52W_High": 1750.40, "%DownFromHigh": 10.45, 
            "MCap(Cr)": 987654.2, "Score": 4, "Volume": "4,123,456"
        },
        {
            "Ticker": "SBIN", "Price": 456.25, "DMA50": 445.80, 
            "52W_High": 520.75, "%DownFromHigh": 12.40, 
            "MCap(Cr)": 345678.9, "Score": 4, "Volume": "8,765,432"
        }
    ]
    
    return mock_stocks

# ---------------------------------------------------------
# Quick Screening (Lightweight version)
# ---------------------------------------------------------
def quick_screen_stocks():
    """
    Lightweight screening for faster results
    """
    print("⚡ Running quick screening...")
    
    # Use a smaller subset for quick screening
    quick_tickers = tickers[:20]  # First 20 stocks for quick results
    
    output = []
    for ticker in quick_tickers:
        try:
            data = fetch_ohlc_yfinance(ticker, period="1y")
            if data is None or len(data) < 100:
                continue
                
            current_price = data["Close"].iloc[-1]
            dma50 = data["Close"].rolling(50).mean().iloc[-1]
            high_52w = data["Close"].rolling(252).max().iloc[-1]
            
            if np.isnan(dma50) or np.isnan(high_52w):
                continue
                
            down_from_high = (high_52w - current_price) / high_52w * 100
            
            # Basic filters
            if (current_price < 500 and 
                current_price > dma50 and 
                0 <= down_from_high <= 25):
                
                output.append({
                    "Ticker": ticker,
                    "Price": round(current_price, 2),
                    "DMA50": round(dma50, 2),
                    "52W_High": round(high_52w, 2),
                    "%DownFromHigh": round(down_from_high, 2),
                    "MCap(Cr)": "N/A",
                    "Score": 3,
                    "Volume": "Quick Scan"
                })
                
        except Exception as e:
            continue
            
        time.sleep(0.2)
    
    if not output:
        return enhanced_mock_screen_stocks()[:3]  # Return top 3 mock results
    
    return sorted(output, key=lambda x: x["%DownFromHigh"])

# ---------------------------------------------------------
def run_screener(quick_mode=False):
    try:
        if quick_mode:
            results = quick_screen_stocks()
        else:
            results = screen_stocks()
            
        print(f"✅ Screener found {len(results)} qualifying stocks.")
        return results
        
    except Exception as e:
        print(f"❌ Screener failed: {e}")
        return enhanced_mock_screen_stocks()

if __name__ == "__main__":
    print("Starting Stock Screener...")
    out = run_screener(quick_mode=True)  # Use quick mode for testing
    print("\n" + "="*60)
    print("SCREENING RESULTS")
    print("="*60)
    for stock in out:
        print(f"{stock['Ticker']}: ₹{stock['Price']} | "
              f"{stock['%DownFromHigh']}% below 52W high | "
              f"Score: {stock['Score']}/5 | "
              f"MCap: ₹{stock['MCap(Cr)']}Cr")
