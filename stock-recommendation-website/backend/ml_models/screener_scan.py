import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
from nselib import capital_market
from nselib import market_data

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
# Fetch OHLC using NSELIB (deliverable & price-volume)
# ---------------------------------------------------------
def fetch_ohlc(symbol, months=18):
    end = datetime.now()
    start = end - timedelta(days=30 * months)

    try:
        df = capital_market.price_volume_and_deliverable_position_data(
            symbol=symbol,
            from_date=start.strftime("%d-%m-%Y"),
            to_date=end.strftime("%d-%m-%Y")
        )

        if df is None or df.empty:
            print(f"⚠️ No OHLC for {symbol}")
            return None

        df = df.rename(columns={
            "CH_TIMESTAMP": "Date",
            "OPEN_PRICE": "Open",
            "HIGH_PRICE": "High",
            "LOW_PRICE": "Low",
            "CLOSE_PRICE": "Close",
            "TTL_TRD_QNTY": "Volume"
        })

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()

        return df[["Open", "High", "Low", "Close", "Volume"]]

    except Exception as e:
        print(f"❌ OHLC fetch failed for {symbol}: {e}")
        return None

# ---------------------------------------------------------
# Fetch market cap table once
# ---------------------------------------------------------
def fetch_market_caps():
    try:
        df = market_data.equity_market_capitalization()
        df = df.rename(columns={"symbol": "Ticker"})
        df = df.set_index("Ticker")
        return df
    except Exception as e:
        print(f"❌ Market cap fetch failed: {e}")
        return None

# ---------------------------------------------------------
# Screening logic
# ---------------------------------------------------------
def screen_stocks():
    output = []
    mcaps = fetch_market_caps()

    if mcaps is None:
        print("❌ Could not fetch market caps.")
        return output

    for ticker in tickers:
        data = fetch_ohlc(ticker)
        if data is None or len(data) < 200:
            continue

        # indicators
        data["DMA50"]  = data["Close"].rolling(50).mean()
        data["52W_High"] = data["Close"].rolling(252).max()

        try:
            current_price = float(data["Close"].iloc[-1])
            dma50        = float(data["DMA50"].iloc[-1])
            high_52w     = float(data["52W_High"].iloc[-1])
        except:
            continue

        if np.isnan(dma50) or np.isnan(high_52w):
            continue

        down_from_high = (high_52w - current_price) / high_52w * 100

        if ticker not in mcaps.index:
            print(f"⚠️ No MCap for {ticker}")
            continue

        try:
            market_cap = float(mcaps.loc[ticker]["mktCap"])
        except:
            continue

        # Filters
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

        # anti-ban jitter
        time.sleep(0.25 + random.random() * 0.25)

    return output

# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------
def run_screener():
    results = screen_stocks()
    print(f"✅ Screener found {len(results)} stocks.")
    return results

# ---------------------------------------------------------
# Manual debug run
# ---------------------------------------------------------
if __name__ == "__main__":
    out = run_screener()
    print(out)
