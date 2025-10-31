import yfinance as yf
import logging
import time

logging.basicConfig(level=logging.INFO)

TICKERS = [
    "IRCTC.NS","BEL.NS","BHEL.NS","NHPC.NS","PNB.NS","BANKBARODA.NS","IDEA.NS",
    "INDHOTEL.NS","ZEEL.NS","SUNTV.NS","CGPOWER.NS","UNIONBANK.NS","SUZLON.NS",
    "IDFCFIRSTB.NS","TATAMOTORS.NS","HINDCOPPER.NS","DALBHARAT.NS","RVNL.NS",
    "PFC.NS","RECLTD.NS","SAIL.NS","NMDC.NS","TATASTEEL.NS","FEDERALBNK.NS","HINDZINC.NS",
    "SOUTHBANK.NS","FINOPB.NS","IDBI.NS","SGFINANCE.NS","HUHTAMAKI.NS",
    "KARURVYSYA.NS","TNMBL.NS","DCBBANK.NS","UJJIVANSFB.NS","INDOTHAI.NS",
    "LTF.NS","SHRIDIG.NS","CANHSULIFE.NS","M&MFIN.NS","IREDA.NS","SAGILITY.NS",
    "WELSPUNSPEC.NS","FEDFINA.NS","PFS.NS","HINDPETRO.NS","GODIGIT.NS"
]

BATCH_SIZE = 8  # keep low to prevent Yahoo blocking

def safe_download(ticker):
    for attempt in range(3):
        try:
            df = yf.download(
                ticker, period="6mo", interval="1d", progress=False
            )
            if df is None or df.empty:
                logging.warning(f"{ticker}: empty data; retry {attempt+1}/3")
                time.sleep(2)
                continue
            return df
        except Exception as e:
            logging.error(f"{ticker}: {e}, retry {attempt+1}/3")
            time.sleep(2)
    logging.error(f"{ticker}: FAILED after retries")
    return None

def detect_pattern(df):
    # dummy logic — replace later
    return df["Close"].iloc[-1] > df["Close"].mean()

def run_detection():
    matches = []

    for i in range(0, len(TICKERS), BATCH_SIZE):
        batch = TICKERS[i:i+BATCH_SIZE]
        logging.info(f"Processing batch: {batch}")

        for ticker in batch:
            df = safe_download(ticker)
            if df is None:
                continue
            if detect_pattern(df):
                matches.append(ticker)

            time.sleep(1)  # <- ESSENTIAL THROTTLE

        # cooldown between batches
        time.sleep(3)

    logging.info(f"✅ PATTERN MATCHES: {matches}")
    return matches

if __name__ == "__main__":
    run_detection()
