from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.pattern_detector import PatternDetector
import requests
import pandas as pd
import os
import time

cron_bp = Blueprint("cron", __name__)

CRON_SECRET = os.getenv("CRON_SECRET", "my_cron_secret")

# Same ticker list
tickers = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "ITC",
    "LT", "SBIN", "AXISBANK", "BHARTIARTL", "KOTAKBANK", "HINDUNILVR",
    "ASIANPAINT", "SUNPHARMA", "MARUTI", "ULTRACEMCO", "POWERGRID",
    "NTPC", "ONGC", "NESTLEIND", "BAJFINANCE", "BAJAJFINSV", "WIPRO",
    "ADANIENT", "ADANIPORTS", "COALINDIA", "IOC", "TITAN", "HEROMOTOCO",
    "M&M", "TECHM", "JSWSTEEL", "HCLTECH", "BPCL", "BRITANNIA",
    "IRCTC", "BEL", "BHEL", "NHPC", "PNB", "BANKBARODA", "IDEA",
    "INDHOTEL", "ZEEL", "SUNTV", "CGPOWER", "UNIONBANK", "SUZLON",
    "IDFCFIRSTB", "TATAMOTORS", "HINDCOPPER", "DALBHARAT", "RVNL",
    "PFC", "RECLTD", "SAIL", "NMDC", "TATASTEEL", "FEDERALBNK", "HINDZINC",
    "SOUTHBANK", "FINOPB", "IDBI", "SGFINANCE", "HUHTAMAKI",
    "KARURVYSYA", "TNMBL", "DCBBANK", "UJJIVANSFB", "INDOTHAI",
    "LTF", "SHRIDIG", "CANHSULIFE", "M&MFIN", "IREDA", "SAGILITY",
    "WELSPUNSPEC", "FEDFINA", "PFS", "HINDPETRO", "GODIGIT"
]

# Fetch from NSE
def fetch_nse_history(symbol):
    url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from=2023-01-01&to=2099-12-31"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com"
    }

    with requests.Session() as s:
        s.get("https://www.nseindia.com", headers=headers)
        r = s.get(url, headers=headers)
        data = r.json()

    rows = data.get("data", [])
    if not rows:
        return None

    df = pd.DataFrame(rows)
    df["CH_TIMESTAMP"] = pd.to_datetime(df["CH_TIMESTAMP"])
    df = df.set_index("CH_TIMESTAMP")
    df = df.rename(columns={
        "CH_OPENING_PRICE": "Open",
        "CH_CLOSING_PRICE": "Close",
        "CH_TRADE_HIGH_PRICE": "High",
        "CH_TRADE_LOW_PRICE": "Low",
        "CH_TOT_TRADED_QTY": "Volume",
    })
    return df[["Open", "High", "Low", "Close", "Volume"]].sort_index()

@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    detector = PatternDetector()
    matching = []

    for sym in tickers:
        try:
            df = fetch_nse_history(sym)
            if df is None or df.empty:
                print(f"⚠️ Empty NSE data for {sym}")
                continue

            df = df.tail(400)  # mimic 18mo

            res = detector.detect(df, sym)

            if res["matched"]:
                matching.append(sym)

            time.sleep(0.4)  # avoid rate limiting

        except Exception as e:
            print(f"❌ Error processing {sym}: {e}")

    users = User.query.filter_by(is_active=True).all()
    email_service = EmailService()

    for user in users:
        email_service.send_email(
            user.email,
            "Daily Stock Recommendations",
            "Today's picks:\n\n" + ("\n".join(matching) if matching else "No patterns found today.")
        )
        user.last_email_sent = db.func.now()

    db.session.commit()

    return jsonify({
        "sent_to": len(users),
        "matches": matching,
        "tickers_scanned": len(tickers)
    })
