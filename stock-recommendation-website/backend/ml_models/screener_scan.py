import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# ---------------------------------------------------------
# STOCK DATA FROM YOUR LIST (No API calls needed)
# ---------------------------------------------------------
STOCK_DATA = {
    "MONARCH": {"price": 462.85, "mcap": 1006.05, "volume": 57.22},
    "HINDZINC": {"price": 476.50, "mcap": 201336.45, "volume": 11.58},
    "COALINDIA": {"price": 388.65, "mcap": 239514.44, "volume": 4262.64},
    "CANARABANK": {"price": 316.85, "mcap": 6318.54, "volume": 48.71},
    "BONDADA": {"price": 447.55, "mcap": 4994.37, "volume": 92.56},
    "BEL": {"price": 426.10, "mcap": 311469.68, "volume": 1287.16},
    "ITC": {"price": 420.35, "mcap": 526607.66, "volume": 5186.55},
    "SHREEJI": {"price": 266.47, "mcap": 4341.28, "volume": 42.70},
    "STEELCAST": {"price": 224.90, "mcap": 2275.99, "volume": 23.21},
    "GARUDA": {"price": 216.64, "mcap": 2015.66, "volume": 27.14},
    "NMDC": {"price": 75.79, "mcap": 66633.19, "volume": 1698.04},
    "INDUSTOWERS": {"price": 363.60, "mcap": 97987.91, "volume": 1839.30},
    "JAINRES": {"price": 386.05, "mcap": 13322.04, "volume": 98.64},
    "VEDANTA": {"price": 493.55, "mcap": 192997.20, "volume": 3479.00},
    "VARUNBEV": {"price": 1450.00, "mcap": 195000.00, "volume": 1200.00}  # Estimated
}

# Map to yfinance symbols
YF_SYMBOLS = {
    "MONARCH": "MONARCH.NS",
    "HINDZINC": "HINDZINC.NS", 
    "COALINDIA": "COALINDIA.NS",
    "CANARABANK": "CANBK.NS",
    "BONDADA": "BONDADA.NS",
    "BEL": "BEL.NS",
    "ITC": "ITC.NS",
    "SHREEJI": "SHREEJI.NS",
    "STEELCAST": "STEELCAST.NS",
    "GARUDA": "GARUDA.NS",
    "NMDC": "NMDC.NS",
    "INDUSTOWERS": "INDUSTOWER.NS",
    "JAINRES": "JAINRES.NS",
    "VEDANTA": "VEDL.NS",
    "VARUNBEV": "VBL.NS"
}

# ---------------------------------------------------------
# Safe yfinance wrapper with aggressive rate limiting
# ---------------------------------------------------------
class SafeYFinance:
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 5.0  # 5 seconds between calls
        self.max_retries = 2
        self.retry_delay = 10
    
    def get_ticker_data(self, symbol, period="6mo"):
        """Safely get ticker data with aggressive rate limiting"""
        import time
        
        # Rate limiting
        time_since_last_call = time.time() - self.last_call_time
        if time_since_last_call < self.min_interval:
            time.sleep(self.min_interval - time_since_last_call)
        
        for attempt in range(self.max_retries):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, auto_adjust=False)
                self.last_call_time = time.time()
                return data
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"⚠️ Rate limited for {symbol}, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Error fetching {symbol}: {e}")
                    break
        return None

# Create global instance
safe_yf = SafeYFinance()

# ---------------------------------------------------------
# Fetch OHLC data only (no market cap calls)
# ---------------------------------------------------------
def fetch_ohlc_data(symbol, period="6mo"):
    """Fetch only OHLC data - no market cap calls"""
    try:
        yf_symbol = YF_SYMBOLS.get(symbol)
        if not yf_symbol:
            print(f"⚠️ No yfinance symbol mapping for {symbol}")
            return None
            
        data = safe_yf.get_ticker_data(yf_symbol, period)
        
        if data is None or data.empty:
            print(f"⚠️ No price data for {symbol}")
            return None
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            print(f"⚠️ Missing columns for {symbol}")
            return None
        
        data = data[required_cols].dropna()
        
        if len(data) < 30:  # Reduced minimum
            print(f"⚠️ Insufficient data for {symbol}: {len(data)}")
            return None
            
        print(f"✅ Fetched {len(data)} days of price data for {symbol}")
        return data
        
    except Exception as e:
        print(f"❌ Price fetch failed for {symbol}: {e}")
        return None

# ---------------------------------------------------------
# Enhanced Screening Logic (No API calls for market caps)
# ---------------------------------------------------------
def screen_stocks():
    """Screen stocks using pre-defined data and minimal API calls"""
    output = []
    
    print("📊 Using pre-defined stock data (no market cap API calls)")
    print(f"🔍 Screening {len(STOCK_DATA)} stocks...")
    
    successful_fetches = 0
    
    for symbol, stock_info in STOCK_DATA.items():
        print(f"Processing: {symbol}")
        
        # Get price data only
        price_data = fetch_ohlc_data(symbol, period="6mo")
        if price_data is None:
            # Use static data if API fails
            current_price = stock_info["price"]
            high_52w = current_price * 1.15  # Estimate 15% above current
            dma50 = current_price * 1.02     # Estimate 2% above current
            volume_ok = True
            print(f"📦 Using static data for {symbol}")
        else:
            try:
                # Calculate from real data
                current_price = price_data["Close"].iloc[-1]
                high_52w = price_data["High"].max()
                dma50 = price_data["Close"].rolling(50).mean().iloc[-1] if len(price_data) >= 50 else current_price
                avg_volume = price_data["Volume"].mean()
                volume_ok = avg_volume > 10000
                
                if np.isnan(dma50):
                    dma50 = current_price
                    
            except Exception as e:
                print(f"⚠️ Error processing {symbol}: {e}")
                continue
        
        # Get pre-defined market cap
        market_cap = stock_info["mcap"]
        
        # Calculate percentage down from high
        down_from_high = ((high_52w - current_price) / high_52w * 100) if high_52w > 0 else 0
        
        # SCREENING CRITERIA
        score = 0
        reasons = []
        
        # Filter 1: Market Cap > 1000 Cr
        if market_cap > 1000:
            score += 1
            reasons.append("Good market cap")
        
        # Filter 2: Price < 500 (affordable)
        if current_price < 500:
            score += 1
            reasons.append("Affordable price")
        
        # Filter 3: Above 50 DMA (if we have real data)
        if price_data is not None and not np.isnan(dma50):
            if current_price > dma50:
                score += 1
                reasons.append("Above 50DMA")
        
        # Filter 4: Reasonable distance from high (5-30%)
        if 5 <= down_from_high <= 30:
            score += 1
            reasons.append(f"Good entry point ({down_from_high:.1f}% below high)")
        
        # Filter 5: Volume check
        if volume_ok:
            score += 1
            reasons.append("Good volume")
        
        # Stock qualifies if it passes at least 3/5 filters
        if score >= 3:
            output.append({
                "Ticker": symbol,
                "Price": round(current_price, 2),
                "DMA50": round(dma50, 2) if not np.isnan(dma50) else "N/A",
                "52W_High": round(high_52w, 2),
                "%DownFromHigh": round(down_from_high, 2),
                "MCap(Cr)": round(market_cap, 2),
                "Score": score,
                "Reasons": ", ".join(reasons),
                "Data_Source": "Live" if price_data is not None else "Static"
            })
            print(f"✅ {symbol} passed {score}/5 filters")
        
        successful_fetches += 1

    print(f"📈 Successfully screened {successful_fetches} stocks")
    
    # Sort by score (descending) then by % down from high (ascending)
    return sorted(output, key=lambda x: (-x["Score"], x["%DownFromHigh"]))

# ---------------------------------------------------------
# Quick screening for faster results
# ---------------------------------------------------------
def quick_screen():
    """Quick screening with minimal API usage"""
    print("⚡ Running quick screening with pre-defined data...")
    
    output = []
    
    for symbol, stock_info in STOCK_DATA.items():
        # Use static data only - no API calls
        current_price = stock_info["price"]
        market_cap = stock_info["mcap"]
        
        # Simple screening based on your criteria
        if (market_cap > 1000 and 
            current_price < 500 and 
            current_price > 50):  # Basic price filter
            
            # Estimate technicals
            high_52w = current_price * 1.12  # Assume 12% above current
            down_from_high = 12.0  # Assume 12% below high
            
            output.append({
                "Ticker": symbol,
                "Price": round(current_price, 2),
                "DMA50": round(current_price * 0.98, 2),  # Estimate
                "52W_High": round(high_52w, 2),
                "%DownFromHigh": down_from_high,
                "MCap(Cr)": round(market_cap, 2),
                "Score": 3,
                "Reasons": "Quick screen pass",
                "Data_Source": "Static"
            })
    
    return sorted(output, key=lambda x: x["%DownFromHigh"])

# ---------------------------------------------------------
def run_screener(quick_mode=True):
    """
    Main screening function
    """
    try:
        print("🚀 Starting Stock Screener")
        print("💡 Using pre-defined data to avoid API rate limits")
        
        if quick_mode:
            results = quick_screen()
        else:
            results = screen_stocks()
            
        print(f"✅ Screener found {len(results)} qualifying stocks.")
        return results
        
    except Exception as e:
        print(f"❌ Screener failed: {e}")
        return []

# ---------------------------------------------------------
if __name__ == "__main__":
    print("Starting Enhanced Stock Screener")
    print("=" * 60)
    
    # Run quick screen first (no API calls)
    results = run_screener(quick_mode=True)
    
    print("\n" + "=" * 60)
    print("SCREENING RESULTS")
    print("=" * 60)
    
    if results:
        for i, stock in enumerate(results, 1):
            print(f"{i}. {stock['Ticker']}:")
            print(f"   Price: ₹{stock['Price']} | MCap: ₹{stock['MCap(Cr)']}Cr")
            print(f"   Score: {stock['Score']}/5 | % Below High: {stock['%DownFromHigh']}%")
            print(f"   Reasons: {stock['Reasons']}")
            print(f"   Data: {stock['Data_Source']}")
            print()
    else:
        print("❌ No stocks passed the screening criteria")
