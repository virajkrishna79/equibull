from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.screener_scan import run_screener   # ✅ your screener
import os

cron_bp = Blueprint("cron", __name__)

CRON_SECRET = os.getenv("CRON_SECRET", "my_cron_secret")


@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    # Check secret header
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    # Run screener
    results = run_screener() or []
    tickers = [row["Ticker"] for row in results]

    # Fetch subscribed users
    users = User.query.filter_by(is_active=True).all()

    email_service = EmailService()
    sent_count = 0

    for user in users:
        try:
            if tickers:
                body = (
                    "Today's Stock Picks:\n\n" +
                    "\n".join(tickers) +
                    "\n\n— Powered by NSE Screener Algo"
                )
            else:
                body = "No qualifying stocks today based on screener conditions."

            email_service.send_email(
                user.email,
                "Daily Stock Recommendations",
                body
            )

            user.last_email_sent = db.func.now()
            sent_count += 1

        except Exception as e:
            print(f"Email send error for {user.email}: {e}")

    db.session.commit()

    return jsonify({
        "emails_sent": sent_count,
        "matches": tickers,
        "count": len(tickers),
        "status": "completed"
    }), 200
