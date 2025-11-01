import pandas as pd
from datetime import datetime, timedelta
from nselib import capital_market

# ---------------------------------------------------------
# Fetch recent NSE candles
# ---------------------------------------------------------
def fetch_recent_data(symbol, n=50):
    end = datetime.now()
    start = end - timedelta(days=120)

    try:
        df = capital_market.price_volume_and_deliverable_position_data(
            symbol=symbol,
            from_date=start.strftime("%d-%m-%Y"),
            to_date=end.strftime("%d-%m-%Y")
        )

        if df is None or df.empty:
            return None

        df = df.rename(columns={
            "OPEN_PRICE": "Open",
            "HIGH_PRICE": "High",
            "LOW_PRICE": "Low",
            "CLOSE_PRICE": "Close",
            "TTL_TRD_QNTY": "Volume",
            "CH_TIMESTAMP": "Date"
        })

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df = df[["Open", "High", "Low", "Close", "Volume"]].sort_index()

        return df.tail(n)

    except Exception:
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

        return signals
