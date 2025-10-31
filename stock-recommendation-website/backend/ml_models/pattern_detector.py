import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm

class PatternDetector:
    """Detects technical patterns based on your defined filters."""

    def __init__(self):
        # Master NSE list (can move to utils.symbols later)
        self.tickers = list(set([
            "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","ITC.NS",
            "LT.NS","SBIN.NS","AXISBANK.NS","BHARTIARTL.NS","KOTAKBANK.NS","HINDUNILVR.NS",
            "ASIANPAINT.NS","SUNPHARMA.NS","MARUTI.NS","ULTRACEMCO.NS","POWERGRID.NS",
            "NTPC.NS","ONGC.NS","NESTLEIND.NS","BAJFINANCE.NS","BAJAJFINSV.NS","WIPRO.NS",
            "ADANIENT.NS","ADANIPORTS.NS","COALINDIA.NS","IOC.NS","TITAN.NS","HEROMOTOCO.NS",
            "M&M.NS","TECHM.NS","JSWSTEEL.NS","HCLTECH.NS","BPCL.NS","BRITANNIA.NS",
            "IRCTC.NS","BEL.NS","BHEL.NS","NHPC.NS","PNB.NS","BANKBARODA.NS","IDEA.NS",
            "INDHOTEL.NS","ZEEL.NS","SUNTV.NS","CGPOWER.NS","UNIONBANK.NS","SUZLON.NS",
            "IDFCFIRSTB.NS","TATAMOTORS.NS","HINDCOPPER.NS","DALBHARAT.NS","RVNL.NS",
            "PFC.NS","RECLTD.NS","SAIL.NS","NMDC.NS","TATASTEEL.NS","FEDERALBNK.NS","HINDZINC.NS",
            "SOUTHBANK.NS","FINOPB.NS","IDBI.NS","SGFINANCE.NS","HUHTAMAKI.NS",
            "KARURVYSYA.NS","TNMBL.NS","DCBBANK.NS","UJJIVANSFB.NS","INDOTHAI.NS",
            "LTF.NS","SHRIDIG.NS","CANHSULIFE.NS","M&MFIN.NS","IREDA.NS","SAGILITY.NS",
            "WELSPUNSPEC.NS","FEDFINA.NS","PFS.NS","HINDPETRO.NS","GODIGIT.NS"
        ]))

    def run_scan(self):
        """Runs the screener on all tickers and returns matched ones."""
        results = []
        for ticker in tqdm(self.tickers, desc="Scanning NSE stocks"):
            try:
                data = yf.download(ticker, period="18mo", interval="1d", progress=False)
                if data.empty or len(data) < 252:
                    continue

                data["DMA50"] = data["Close"].rolling(50).mean()
                data["52W_High"] = data["Close"].rolling(252).max()

                price = float(data["Close"].iloc[-1])
                dma50 = float(data["DMA50"].iloc[-1])
                high_52w = float(data["52W_High"].iloc[-1])

                if np.isnan(dma50) or np.isnan(high_52w):
                    continue

                down_from_high = (high_52w - price) / high_52w * 100
                info = yf.Ticker(ticker).info
                mcap = info.get("marketCap")
                if not mcap:
                    continue

                mcap_cr = mcap / 1e7

                if (
                    mcap_cr > 1000 and
                    price < 500 and
                    price > dma50 and
                    0 <= down_from_high <= 100
                ):
                    results.append({
                        "Ticker": ticker.replace(".NS", ""),
                        "Price": round(price, 2),
                        "DMA50": round(dma50, 2),
                        "52W_High": round(high_52w, 2),
                        "%DownFromHigh": round(down_from_high, 2),
                        "MCap(Cr)": round(mcap_cr, 1)
                    })
            except Exception:
                continue
        return results
