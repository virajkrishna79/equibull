import pandas as pd
import numpy as np
import time
import random
import requests
from datetime import datetime, timedelta

# ---------------------------------------------------------
# TICKERS
# ---------------------------------------------------------
tickers = list(set([
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","ITC",
    "LT","SBIN","AXISBANK","BHARTIARTL","KOTAKBANK","HINDUNILVR",
    "ASIANPAINT","SUNPHARMA","MARUTI","ULTRACEMCO","POWERGRID",
    "NTPC","ONGC","NESTLEIND","BAJFINANCE","BAJAJFINSV","WIPRO",
    "ADANIENT","ADANIPORTS","COALINDIA","IOC","TITAN","HEROMOTOCO",
    "M&M","TECHM","JSWSTEEL","HCLTECH","BPCL","BRITANNIA",
    "IRCTC","BEL","BHEL","NHPC","PNB","BANKBARODA","IDEA",
    "INDHOTEL","ZEEL","SUNTV","CGPOWER","UNIONBANK","SUZLON",
    "IDFCFIRSTB","TATAMOTORS","HINDCOPPER","DALBHARAT","RVNL",
    "PFC","RECLTD","SAIL","NMDC","TATASTEEL","FEDERALBNK","HINDZINC",
    "SOUTHBANK","FINOPB","IDBI","SGFINANCE","HUHTAMAKI","KARURVYSYA",
    "TNMBL","DCBBANK","UJJIVANSFB","INDOTHAI","LTF","SHRIDIG",
    "CANHSULIFE","M&MFIN","IREDA","SAGILITY","WELSPUNSPEC","FEDFINA",
    "PFS","HINDPETRO","GODIGIT"
]))

# ---------------------------------------------------------
# NSE API Helper with session management
# ---------------------------------------------------------
class NSEHelper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/'
        })
        self.base_url = "https://www.nseindia.com"
        self._setup_session()
    
    def _setup_session(self):
        """Initialize session by visiting main page first"""
        try:
            self.session.get(f"{self.base_url}/", timeout=10)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Session setup failed: {e}")
    
    def nsefetch(self, url):
        """Replacement for nsefetch using requests"""
        try:
            # If relative URL, make it absolute
            if url.startswith('/'):
                url = f"{self.base_url}{url}"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Handle both JSON and CSV responses
            if 'application/json' in response.headers.get('content-type', ''):
                return response.json()
            else:
                # For CSV or other formats, return text
                return response.text
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {url}: {e}")
            return None

# Create global NSE helper instance
nse_helper = NSEHelper()

# ---------------------------------------------------------
# Fetch OHLC using the new nsefetch replacement
# ---------------------------------------------------------
def fetch_ohlc(symbol, months=18):
    end = datetime.now()
    start = end - timedelta(days=30 * months)

    url = (
        f"/api/historical/cm/equity?"
        f"symbol={symbol}&series=[\"EQ\"]&from={start.strftime('%d-%m-%Y')}"
        f"&to={end.strftime('%d-%m-%Y')}"
    )

    try:
        data = nse_helper.nsefetch(url)
        if not data or "data" not in data or not data["data"]:
            print(f"⚠️ No OHLC data for {symbol}")
            return None

        df = pd.DataFrame(data["data"])
        
        # Handle different column name formats from NSE API
        column_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'timestamp' in col_lower:
                column_map[col] = "Date"
            elif 'open' in col_lower:
                column_map[col] = "Open"
            elif 'high' in col_lower:
                column_map[col] = "High"  
            elif 'low' in col_lower:
                column_map[col] = "Low"
            elif 'close' in col_lower:
                column_map[col] = "Close"
            elif 'volume' in col_lower or 'qty' in col_lower:
                column_map[col] = "Volume"
        
        df = df.rename(columns=column_map)
        
        # Ensure we have the required columns
        required_cols = ["Date", "Open", "High", "Low", "Close"]
        if not all(col in df.columns for col in required_cols):
            print(f"⚠️ Missing required columns for {symbol}")
            return None

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()

        # Convert numeric columns
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    except Exception as e:
        print(f"❌ OHLC fetch failed for {symbol}: {e}")
        return None

# ---------------------------------------------------------
# Fetch Market Caps (Full NSE Table)
# ---------------------------------------------------------
def fetch_market_caps():
    try:
        url = "/api/equity-market-capitalization"
        data = nse_helper.nsefetch(url)
        
        if not data or "data" not in data:
            print("❌ No market cap data received")
            return None
            
        df = pd.DataFrame(data["data"])
        
        # Find the symbol column (could be 'symbol', 'SYMBOL', etc.)
        symbol_col = None
        for col in df.columns:
            if 'symbol' in col.lower():
                symbol_col = col
                break
        
        if not symbol_col:
            print("❌ Could not find symbol column in market cap data")
            return None
            
        df = df.rename(columns={symbol_col: "Ticker"})
        df = df.set_index("Ticker")
        return df
        
    except Exception as e:
        print(f"❌ Market cap fetch failed: {e}")
        return None

# ---------------------------------------------------------
# Alternative: Fallback screening with mock data for testing
# ---------------------------------------------------------
def mock_screen_stocks():
    """Fallback function that returns mock data for testing"""
    print("🔄 Using mock data for screening (NSE API unavailable)")
    
    mock_stocks = [
        {"Ticker": "RELIANCE", "Price": 2456.75, "DMA50": 2400.50, "52W_High": 2800.25, "%DownFromHigh": 12.25, "MCap(Cr)": 1567892.1},
        {"Ticker": "TCS", "Price": 3456.25, "DMA50": 3400.75, "52W_High": 3800.50, "%DownFromHigh": 9.05, "MCap(Cr)": 1276543.8},
        {"Ticker": "INFY", "Price": 1678.90, "DMA50": 1650.25, "52W_High": 1850.75, "%DownFromHigh": 9.29, "MCap(Cr)": 687654.3},
    ]
    
    return mock_stocks

# ---------------------------------------------------------
# Screening logic
# ---------------------------------------------------------
def screen_stocks():
    output = []
    
    print("📊 Fetching market capitalization data...")
    mcaps = fetch_market_caps()

    if mcaps is None:
        print("❌ Could not fetch market caps, using fallback...")
        return mock_screen_stocks()

    print(f"🔍 Screening {len(tickers)} stocks...")
    
    successful_fetches = 0
    for i, ticker in enumerate(tickers):
        print(f"Processing {i+1}/{len(tickers)}: {ticker}")
        
        data = fetch_ohlc(ticker)
        if data is None or len(data) < 200:
            continue

        successful_fetches += 1
        
        # Calculate indicators
        data["DMA50"] = data["Close"].rolling(50).mean()
        data["52W_High"] = data["Close"].rolling(252).max()

        try:
            current_price = float(data["Close"].iloc[-1])
            dma50 = float(data["DMA50"].iloc[-1])
            high_52w = float(data["52W_High"].iloc[-1])
        except (ValueError, IndexError) as e:
            print(f"⚠️ Error calculating indicators for {ticker}: {e}")
            continue

        if np.isnan(dma50) or np.isnan(high_52w):
            continue

        down_from_high = (high_52w - current_price) / high_52w * 100

        if ticker not in mcaps.index:
            print(f"⚠️ No MCap data for {ticker}")
            continue

        try:
            # Find market cap column (could be 'mktCap', 'marketCap', etc.)
            mcap_col = None
            for col in mcaps.columns:
                if 'mktcap' in col.lower() or 'marketcap' in col.lower():
                    mcap_col = col
                    break
            
            if not mcap_col:
                print(f"⚠️ No market cap column found for {ticker}")
                continue
                
            market_cap = float(mcaps.loc[ticker][mcap_col])
        except (ValueError, KeyError) as e:
            print(f"⚠️ Error reading market cap for {ticker}: {e}")
            continue

        # FILTERS
        if (
            market_cap > 1000 and
            current_price < 500 and
            current_price > dma50 and
            0 <= down_from_high <= 100
        ):
            output.append({
                "Ticker": ticker,
                "Price": round(current_price, 2),
                "DMA50": round(dma50, 2),
                "52W_High": round(high_52w, 2),
                "%DownFromHigh": round(down_from_high, 2),
                "MCap(Cr)": round(market_cap, 1)
            })
            print(f"✅ {ticker} passed screening")

        # Rate limiting to avoid being blocked
        time.sleep(0.5 + random.random() * 0.5)

    print(f"📈 Successfully processed {successful_fetches} stocks")
    return sorted(output, key=lambda x: x["%DownFromHigh"])

# ---------------------------------------------------------
def run_screener():
    try:
        results = screen_stocks()
        print(f"✅ Screener found {len(results)} qualifying stocks.")
        return results
    except Exception as e:
        print(f"❌ Screener failed: {e}")
        return mock_screen_stocks()

if __name__ == "__main__":
    out = run_screener()
    print("\n" + "="*50)
    print("SCREENING RESULTS")
    print("="*50)
    for stock in out:
        print(f"{stock['Ticker']}: ₹{stock['Price']} | {stock['%DownFromHigh']}% below 52W high | MCap: ₹{stock['MCap(Cr)']}Cr")
