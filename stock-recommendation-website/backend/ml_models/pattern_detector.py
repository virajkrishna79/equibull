import pandas as pd
from datetime import datetime, timedelta
from nselib import capital_market

# ---------------------------------------------------------
# Helper to fetch last N candles
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
        df['Close'] = df['Close Price']
        df['Open'] = df['Open Price']
        df['High'] = df['High Price']
        df['Low']  = df['Low Price']
        return df.tail(n)
    except:
        return None

# ---------------------------------------------------------
# Very basic pattern examples
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
