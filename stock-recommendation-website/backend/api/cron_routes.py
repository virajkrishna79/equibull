from flask import Blueprint, jsonify, request
from app import db
from models.user import User
from services.email_service import EmailService
from ml_models.screener_scan import run_screener  # <-- NEW IMPORT
import os

cron_bp = Blueprint("cron", __name__)

CRON_SECRET = os.getenv("CRON_SECRET", "my_cron_secret")

@cron_bp.route("/run-detection", methods=["POST"])
def run_detection():
    secret = request.headers.get("X-CRON-SECRET")
    if secret != CRON_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    # Run the screener logic
    results = run_screener()
    picks = [row["Ticker"] for row in results]

    # Send email to all active users
    users = User.query.filter_by(is_active=True).all()
    email_service = EmailService()

    for user in users:
        email_content = (
            "Today's Stock Picks:\n\n" +
            ("\n".join(picks) if picks else "No qualifying stocks today.")
        )

        email_service.send_email(
            user.email,
            "Daily Stock Recommendations",
            email_content
        )

        user.last_email_sent = db.func.now()

    db.session.commit()

    return jsonify({
        "sent_to": len(users),
        "matches": picks,
        "total_found": len(picks)
    })
