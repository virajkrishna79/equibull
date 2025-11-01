import pandas as pd
import time
from datetime import datetime, timedelta
from nsepython import nsefetch

# ---------------------------------------------------------
# Fetch last N candles from NSE charts API
# ---------------------------------------------------------
def fetch_recent_data(symbol, n=50):
    end = datetime.now()
    start = end - timedelta(days=120)

    url = (
        f"https://www.nseindia.com/api/historical/cm/equity?"
        f"symbol={symbol}&series=[\"EQ\"]&from={start.strftime('%d-%m-%Y')}"
        f"&to={end.strftime('%d-%m-%Y')}&csv=true"
    )

    try:
        data = nsefetch(url)
        if not data or "data" not in data or not data["data"]:
            print(f"⚠️ No data returned for {symbol}")
            return None

        df = pd.DataFrame(data["data"])
        df = df.rename(columns={
            "CH_TIMESTAMP": "Date",
            "CH_OPENING_PRICE": "Open",
            "CH_TRADE_HIGH_PRICE": "High",
            "CH_TRADE_LOW_PRICE": "Low",
            "CH_CLOSING_PRICE": "Close",
            "CH_TOT_TRADED_QTY": "Volume",
        })

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df = df.sort_index()
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        return df.tail(n)

    except Exception as e:
        print(f"❌ Fetch failed for {symbol}: {e}")
        return None


# ---------------------------------------------------------
# Pattern examples
# ---------------------------------------------------------
def bullish_engulfing(df):
    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev['Close'] < prev['Open'] and
        curr['Close'] > curr['Open'] and
        curr['Close'] > prev['Open'] and
        curr['Open'] < prev['Close']
    )


def recent_breakout(df):
    if len(df) < 10:
        return False

    recent = df['Close'].iloc[-1]
    prev_high = df['Close'].iloc[:-1].max()

    return recent > prev_high


# ---------------------------------------------------------
# Detector
# ---------------------------------------------------------
class PatternDetector:

    def detect(self, tickers):
        signals = {}

        for t in tickers:
            df = fetch_recent_data(t)
            if df is None or df.empty:
                continue

            found = []

            if bullish_engulfing(df):
                found.append("Bullish Engulfing")

            if recent_breakout(df):
                found.append("Recent Breakout")

            if found:
                signals[t] = found

            time.sleep(0.35)  # important: helps avoid NSE blocking

        return signals


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    tickers = [
        "TCS", "WIPRO", "TITAN", "SBIN", "INFY",
        "TECHM", "MARUTI", "ULTRACEMCO", "ONGC"
    ]

    detector = PatternDetector()
    results = detector.detect(tickers)

    print("\n=== PATTERN RESULTS ===")
    print(results)
