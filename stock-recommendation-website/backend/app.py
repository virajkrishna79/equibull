from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Database URL
db_url = os.getenv('DATABASE_URL', 'sqlite:///stock_recommendations.db')

# Fix old Heroku-style URLs
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# ======================
# Imports after db init
# ======================
from models.user import User
from api.routes import main_bp, api_bp
from api.cron_routes import cron_bp

# ======================
# Blueprint registration
# ======================
app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(cron_bp, url_prefix='/cron')

# ======================
# DB init
# ======================
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("DB init error:", e)

# ======================
# Error handlers
# ======================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ======================
# Run
# ======================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)
