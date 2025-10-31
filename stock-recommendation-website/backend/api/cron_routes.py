from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.pattern_detector import PatternDetector
import yfinance as yf
import os

cron_bp = Blueprint("cron", __name__)

CRON_SECRET = os.getenv("CRON_SECRET", "my_cron_secret")

# Full ticker universe
tickers = [
    # Previous main universe
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

    # Newly added from fundamentals table
    "SOUTHBANK.NS","FINOPB.NS","IDBI.NS","SGFINANCE.NS","HUHTAMAKI.NS",
    "KARURVYSYA.NS","TNMBL.NS","DCBBANK.NS","UJJIVANSFB.NS","INDOTHAI.NS",
    "LTF.NS","SHRIDIG.NS","CANHSULIFE.NS","M&MFIN.NS","IREDA.NS","SAGILITY.NS",
    "WELSPUNSPEC.NS","FEDFINA.NS","PFS.NS","HINDPETRO.NS","GODIGIT.NS"
]


@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    # --- Security Check ---
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    detector = PatternDetector()
    matching = []

    for sym in tickers:
        try:
            df = yf.download(sym, period="18mo", interval="1d", progress=False)
            if df.empty:
                print(f"⚠️ Empty data for {sym}")
                continue

            res = detector.detect(df, sym)

            if res["matched"]:
                matching.append(sym)

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
