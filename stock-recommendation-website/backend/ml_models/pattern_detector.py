import yfinance as yf
import numpy as np
import pandas as pd


class PatternDetector:
    def __init__(self):
        # ✅ Your exact tickers
        self.tickers = [
            "IRCTC.NS","BEL.NS","BHEL.NS","NHPC.NS","PNB.NS","BANKBARODA.NS","IDEA.NS",
            "INDHOTEL.NS","ZEEL.NS","SUNTV.NS","CGPOWER.NS","UNIONBANK.NS","SUZLON.NS",
            "IDFCFIRSTB.NS","TATAMOTORS.NS","HINDCOPPER.NS","DALBHARAT.NS","RVNL.NS",
            "PFC.NS","RECLTD.NS","SAIL.NS","NMDC.NS","TATASTEEL.NS","FEDERALBNK.NS","HINDZINC.NS",
            "SOUTHBANK.NS","FINOPB.NS","IDBI.NS","SGFINANCE.NS","HUHTAMAKI.NS",
            "KARURVYSYA.NS","TNMBL.NS","DCBBANK.NS","UJJIVANSFB.NS","INDOTHAI.NS",
            "LTF.NS","SHRIDIG.NS","CANHSULIFE.NS","M&MFIN.NS","IREDA.NS","SAGILITY.NS",
            "WELSPUNSPEC.NS","FEDFINA.NS","PFS.NS","HINDPETRO.NS","GODIGIT.NS"
        ]

        self.lookback_days = 200

    def fetch_data(self, ticker):
        try:
            data = yf.download(
                ticker,
                period=f"{self.lookback_days}d",
                interval="1d",
                progress=False
            )

            if data is None or data.empty:
                return None

            data.dropna(inplace=True)
            return data

        except Exception:
            return None

    def detect_cup_and_handle(self, df):
        closes = df["Close"].values
        if len(closes) < 60:
            return False

        norm = (closes - closes.min()) / (closes.max() - closes.min())
        left = norm[:len(norm)//2].mean()
        right = norm[len(norm)//2:].mean()
        bottom = norm.min()

        return left > bottom and right > bottom and bottom < 0.4

    def detect_breakout(self, df):
        closes = df["Close"]
        recent = closes[-1]
        last_20_high = closes[-20:].max()
        return recent > last_20_high

    def run(self):
        matches = []

        for ticker in self.tickers:
            df = self.fetch_data(ticker)
            if df is None:
                continue

            cup = self.detect_cup_and_handle(df)
            breakout = self.detect_breakout(df)

            if cup or breakout:
                matches.append({
                    "ticker": ticker,
                    "cup": cup,
                    "breakout": breakout
                })

        return matches


# Debug run support
if __name__ == "__main__":
    detector = PatternDetector()
    print(detector.run())
