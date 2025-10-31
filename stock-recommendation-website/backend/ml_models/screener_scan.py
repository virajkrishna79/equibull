import pandas as pd
import numpy as np
from nselib import capital_market
from datetime import datetime, timedelta

# ---------------------------------------------------------
# TICKERS (NO .NS ANYMORE)
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
    "SOUTHBANK","FINOPB","IDBI","SGFINANCE","HUHTAMAKI",
    "KARURVYSYA","TNMBL","DCBBANK","UJJIVANSFB","INDOTHAI",
    "LTF","SHRIDIG","CANHSULIFE","M&MFIN","IREDA","SAGILITY",
    "WELSPUNSPEC","FEDFINA","PFS","HINDPETRO","GODIGIT"
]))

# ---------------------------------------------------------
# Fetch OHLC helper
# ---------------------------------------------------------
def fetch_ohlc(symbol: str, months: int = 18):
    end = datetime.now()
    start = end - timedelta(days=30 * months)

    try:
        df = capital_market.price_volume_and_deliverable_position_data(
            symbol=symbol,
            from_date=start.strftime("%d-%m-%Y"),
            to_date=end.strftime("%d-%m-%Y")
        )
        if df is None or df.empty:
            return None

        df['Close'] = df['Close Price']
        return df
    except:
        return None

# ---------------------------------------------------------
# Market cap helper
# ---------------------------------------------------------
def fetch_market_cap(symbol: str):
    try:
        df = capital_market.equity_market_capitalisation()
        row = df[df["Symbol"] == symbol]
        if row.empty:
            return None
        return float(row["Market Cap (Rs. Cr)"].iloc[0])
    except:
        return None

# ---------------------------------------------------------
# Main screening logic
# ---------------------------------------------------------
def screen_stocks():
    results = []

    for ticker in tickers:
        data = fetch_ohlc(ticker)
        if data is None or len(data) < 252:
            continue

        # Compute DMA & 52W High
        data["DMA50"] = data["Close"].rolling(50).mean()
        data["52W_High"] = data["Close"].rolling(252).max()

        current_price = float(data["Close"].iloc[-1])
        dma50 = float(data["DMA50"].iloc[-1])
        high_52w = float(data["52W_High"].iloc[-1])

        if np.isnan(dma50) or np.isnan(high_52w):
            continue

        down_from_high = (high_52w - current_price) / high_52w * 100

        market_cap = fetch_market_cap(ticker)
        if market_cap is None:
            continue

        # APPLY FILTERS
        if (
            market_cap > 1000 and
            current_price < 500 and
            current_price > dma50 and
            0 <= down_from_high <= 100
        ):
            results.append({
                "Ticker": ticker,
                "Price": round(current_price, 2),
                "DMA50": round(dma50, 2),
                "52W_High": round(high_52w, 2),
                "%DownFromHigh": round(down_from_high, 2),
                "MCap(Cr)": round(market_cap, 1)
            })

    return results

if __name__ == "__main__":
    out = screen_stocks()
    print(out)
