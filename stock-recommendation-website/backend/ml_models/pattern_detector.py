import yfinance as yf
import pandas as pd
import numpy as np

# ✅ Curated NSE tickers (final list)
tickers = [
    "IRCTC.NS","BEL.NS","BHEL.NS","NHPC.NS","PNB.NS","BANKBARODA.NS","IDEA.NS",
    "INDHOTEL.NS","ZEEL.NS","SUNTV.NS","CGPOWER.NS","UNIONBANK.NS","SUZLON.NS",
    "IDFCFIRSTB.NS","TATAMOTORS.NS","HINDCOPPER.NS","DALBHARAT.NS","RVNL.NS",
    "PFC.NS","RECLTD.NS","SAIL.NS","NMDC.NS","TATASTEEL.NS","FEDERALBNK.NS","HINDZINC.NS",
    "SOUTHBANK.NS","FINOPB.NS","IDBI.NS","SGFINANCE.NS","HUHTAMAKI.NS",
    "KARURVYSYA.NS","TNMBL.NS","DCBBANK.NS","UJJIVANSFB.NS","INDOTHAI.NS",
    "LTF.NS","SHRIDIG.NS","CANHSULIFE.NS","M&MFIN.NS","IREDA.NS","SAGILITY.NS",
    "WELSPUNSPEC.NS","FEDFINA.NS","PFS.NS","HINDPETRO.NS","GODIGIT.NS"
]

tickers = list(set(tickers))  # remove duplicates
class PatternDetector:
    def __init__(self):
        pass

    def detect(self, df):
        return detect_patterns(df)

def screen_stocks():
    results = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="18mo", interval="1d", progress=False)
            if data.empty or len(data) < 252:
                continue

            data["DMA50"] = data["Close"].rolling(50).mean()
            data["52W_High"] = data["Close"].rolling(252).max()

            current_price = float(data["Close"].iloc[-1])
            dma50 = float(data["DMA50"].iloc[-1])
            high_52w = float(data["52W_High"].iloc[-1])

            if np.isnan(dma50) or np.isnan(high_52w):
                continue

            down_from_high = (high_52w - current_price) / high_52w * 100

            info = yf.Ticker(ticker).info
            raw_cap = info.get("marketCap")
            if raw_cap is None:
                continue

            market_cap = float(raw_cap) / 1e7  # convert to crores INR

            # ✅ Screener rules
            if (
                market_cap > 1000 and
                current_price < 500 and
                current_price > dma50 and
                0 <= down_from_high <= 100
            ):
                results.append({
                    "Ticker": ticker.replace(".NS",""),
                    "Price": round(current_price,2),
                    "DMA50": round(dma50,2),
                    "52W_High": round(high_52w,2),
                    "%DownFromHigh": round(down_from_high,2),
                    "MCap(Cr)": round(market_cap,1)
                })

        except Exception:
            continue

    return results

if __name__ == "__main__":
    matches = screen_stocks()
    print(matches)

