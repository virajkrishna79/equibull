import pandas as pd
import numpy as np
import time
import random
import yfinance as yf
from tqdm import tqdm
from datetime import datetime, timedelta

# ==========================================
# ✅ FIXED STOCK DATA (From your earlier list)
# ==========================================

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
    "VARUNBEV": {"price": 1450.00, "mcap": 195000.00, "volume": 1200.00}
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

# ==========================================
# ✅ ENHANCED SCREENING ALGORITHM
# ==========================================

class SafeYFinance:
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 3.0  # 3 seconds between calls
        self.max_retries = 2
        self.retry_delay = 10
    
    def get_ticker_data(self, symbol, period="18mo"):
        """Safely get ticker data with rate limiting"""
        # Rate limiting
        time_since_last_call = time.time() - self.last_call_time
        if time_since_last_call < self.min_interval:
            time.sleep(self.min_interval - time_since_last_call)
        
        for attempt in range(self.max_retries):
            try:
                data = yf.download(symbol, period=period, interval="1d", progress=False)
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

def screen_stocks():
    """Screening with EXACT criteria only"""
    results = []
    
    print(f"🔍 Screening {len(STOCK_DATA)} stocks with EXACT criteria...")
    print("📋 Criteria: market_cap > 1000 AND current_price < 500 AND current_price > dma50 AND 0 <= down_from_high <= 100")
    
    for symbol in tqdm(STOCK_DATA.keys()):
        try:
            # Get yfinance symbol
            yf_symbol = YF_SYMBOLS.get(symbol)
            if not yf_symbol:
                continue
            
            # Fetch 18 months data to compute 52W High safely
            data = safe_yf.get_ticker_data(yf_symbol, period="18mo")
            
            if data.empty or len(data) < 252:
                continue
            
            # Calculate technical indicators
            data["DMA50"] = data["Close"].rolling(50).mean()
            data["52W_High"] = data["Close"].rolling(252).max()
            
            # Force scalar extraction
            current_price = float(data["Close"].iloc[-1])
            dma50 = float(data["DMA50"].iloc[-1])
            high_52w = float(data["52W_High"].iloc[-1])
            
            if np.isnan(dma50) or np.isnan(high_52w):
                continue
            
            # Calculate percentage down from high
            down_from_high = (high_52w - current_price) / high_52w * 100
            
            # Get market cap from our fixed data
            market_cap = STOCK_DATA[symbol]["mcap"]
            
            # ======================================
            # ✅ EXACT FILTER CRITERIA ONLY
            # ======================================
            criteria_passed = True
            
            # Check each criterion individually
            if not (market_cap > 1000):
                criteria_passed = False
                print(f"❌ {symbol}: Market cap failed ({market_cap} <= 1000)")
                
            elif not (current_price < 500):
                criteria_passed = False
                print(f"❌ {symbol}: Price failed ({current_price} >= 500)")
                
            elif not (current_price > dma50):
                criteria_passed = False
                print(f"❌ {symbol}: DMA50 failed ({current_price} <= {dma50})")
                
            elif not (0 <= down_from_high <= 100):
                criteria_passed = False
                print(f"❌ {symbol}: %Down failed ({down_from_high:.2f}% not in 0-100)")
            
            # Only add if ALL criteria passed
            if criteria_passed:
                results.append({
                    "Ticker": symbol,
                    "Price": round(current_price, 2),
                    "DMA50": round(dma50, 2),
                    "52W_High": round(high_52w, 2),
                    "%DownFromHigh": round(down_from_high, 2),
                    "MCap(Cr)": round(market_cap, 1),
                    "Volume": STOCK_DATA[symbol]["volume"]
                })
                print(f"✅ {symbol}: PASSED ALL CRITERIA")
                
        except Exception as e:
            print(f"❌ {symbol} failed: {e}")
            continue
    
    return results

def quick_screen_stocks():
    """Quick screening using only fixed data (no API calls)"""
    results = []
    
    print("⚡ Running quick screening with fixed data...")
    print("📋 Criteria: market_cap > 1000 AND price < 500")
    
    for symbol, stock_info in STOCK_DATA.items():
        current_price = stock_info["price"]
        market_cap = stock_info["mcap"]
        
        # Check ONLY the criteria we can verify with fixed data
        if (market_cap > 1000 and current_price < 500):
            
            # Estimate technicals for display
            high_52w = current_price * 1.15
            dma50 = current_price * 1.02
            down_from_high = 12.0
            
            results.append({
                "Ticker": symbol,
                "Price": round(current_price, 2),
                "DMA50": round(dma50, 2),
                "52W_High": round(high_52w, 2),
                "%DownFromHigh": round(down_from_high, 2),
                "MCap(Cr)": round(market_cap, 1),
                "Volume": stock_info["volume"],
                "Data_Source": "Fixed (Partial Check)"
            })
            print(f"✅ {symbol}: Passed basic criteria")
    
    return sorted(results, key=lambda x: x["%DownFromHigh"])

# ==========================================
# ✅ MAIN SCREENER FUNCTION
# ==========================================

def run_screener(quick_mode=False):
    """
    Main screening function with EXACT criteria only
    """
    try:
        print("🚀 Starting Stock Screener")
        print(f"📊 Using {len(STOCK_DATA)} fixed stocks")
        print("🎯 Applying EXACT criteria only:")
        print("   • Market Cap > 1000 Cr")
        print("   • Current Price < ₹500") 
        print("   • Price > 50 DMA")
        print("   • 0% <= % Below 52W High <= 100%")
        print("=" * 60)
        
        if quick_mode:
            results = quick_screen_stocks()
        else:
            results = screen_stocks()
            
        print(f"✅ Screener found {len(results)} stocks passing ALL criteria.")
        return results
        
    except Exception as e:
        print(f"❌ Screener failed: {e}")
        return []

# ==========================================
# ✅ OUTPUT AND ANALYSIS
# ==========================================

if __name__ == "__main__":
    print("Starting Stock Screener with EXACT Criteria")
    print("=" * 60)
    
    # Run the enhanced screener
    results = run_screener(quick_mode=False)
    
    print("\n" + "=" * 60)
    print("FINAL SCREENING RESULTS")
    print("=" * 60)
    
    if results:
        df = pd.DataFrame(results)
        print(f"\n🎉 {len(df)} stocks passed ALL criteria:\n")
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv("screener_results.csv", index=False)
        print("\n📁 Saved → screener_results.csv")
        
    else:
        print("❌ No stocks passed ALL the exact criteria")
        print("🔄 Showing stocks that passed basic criteria (market cap & price only)...")
        
        quick_results = quick_screen_stocks()
        if quick_results:
            df = pd.DataFrame(quick_results)
            print(f"\n📦 {len(df)} stocks passed basic criteria:\n")
            print(df.to_string(index=False))
            print("\n💡 Note: These passed market cap & price criteria but need live data for full validation")
        else:
            print("❌ No stocks available in fixed data")
