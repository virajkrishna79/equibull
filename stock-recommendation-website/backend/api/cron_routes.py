from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.pattern_detector import PatternDetector
import yfinance as yf

cron_bp = Blueprint("cron", __name__)

# Secret to prevent public access
CRON_SECRET = "my_cron_secret"   # put a real secret in .env

@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    detector = PatternDetector()
    tickers = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "HDFCBANK", "TATAMOTORS", "SBIN"]  # add more later

    matching = []

    for sym in tickers:
        df = yf.download(sym+".NS", period="18mo", interval="1d", progress=False)
        res = detector.detect_pattern(df, sym)
        if res["matched"]:
            matching.append(sym)

    users = User.query.filter_by(is_active=True).all()
    email_service = EmailService()

    for user in users:
        email_service.send_email(
            user.email,
            "Daily Stock Recommendations",
            f"Today's picks:\n\n" + "\n".join(matching)
        )
        user.last_email_sent = db.func.now()

    db.session.commit()

    return jsonify({"sent_to": len(users), "matches": matching})
