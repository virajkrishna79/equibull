from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.pattern_detector import PatternDetector
import yfinance as yf
import os

cron_bp = Blueprint("cron", __name__)

CRON_SECRET = os.getenv("CRON_SECRET")  # Load from environment

@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    # Validate secret
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    detector = PatternDetector()
    tickers = [
        "RELIANCE", "TCS", "ICICIBANK", "INFY",
        "HDFCBANK", "TATAMOTORS", "SBIN"
    ]

    matching = []

    # Run pattern detection
    for sym in tickers:
        df = yf.download(sym + ".NS", period="18mo", interval="1d", progress=False)
        res = detector.detect_pattern(df, sym)
        if res["matched"]:
            matching.append(sym)

    # Send emails to all active users
    users = User.query.filter_by(is_active=True).all()
    email_service = EmailService()

    for user in users:
        email_service.send_email(
            user.email,
            "Daily Stock Recommendations",
            "Today's picks:\n\n" + "\n".join(matching)
        )
        user.last_email_sent = db.func.now()

    db.session.commit()

    return jsonify({
        "sent_to": len(users),
        "matches": matching
    })
