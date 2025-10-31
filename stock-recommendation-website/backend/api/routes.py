from flask import Blueprint, request, jsonify
from models import User, StockRecommendation, NewsArticle
from services.stock_service import StockService
from services.news_service import NewsService
from services.recommendation_service import RecommendationService
from services.email_service import EmailService
from app import db
import logging
import os
from utils.symbols import NIFTY50_SYMBOLS, load_symbol_universe
from ml_models.screener_scan import screen_stocks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize services
stock_service = StockService()
news_service = NewsService()
recommendation_service = RecommendationService()
email_service = EmailService()

@main_bp.route('/')
def index():
    """Health/info root (JSON response to avoid missing template errors)"""
    try:
        news = news_service.get_latest_news(limit=5)
        return jsonify({
            'status': 'ok',
            'service': 'stock-recommendation-api',
            'news_preview': news
        })
    except Exception as e:
        logger.error(f"Error loading homepage: {e}")
        return jsonify({'status': 'ok', 'service': 'stock-recommendation-api', 'news_preview': []})

@main_bp.route('/about')
def about():
    """About page (JSON)"""
    return jsonify({'app': 'stock-recommendation-api', 'about': 'Backend service for stock recommendations and news'})

@api_bp.route('/subscribe', methods=['POST'])
@api_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Subscribe user to stock recommendations"""
    try:
        data = request.get_json(silent=True) or {}
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.is_active:
                return jsonify({'message': 'Email already subscribed'}), 200
            else:
                existing_user.is_active = True
                db.session.commit()
                return jsonify({'message': 'Subscription reactivated successfully'}), 200

        new_user = User(email=email)
        db.session.add(new_user)
        db.session.commit()

        # optional confirmation email
        try:
            email_service.send_confirmation_email(email)
        except Exception as e:
            logger.warning(f"Failed to send confirmation email: {e}")

        return jsonify({'message': 'Subscription successful!'}), 201

    except Exception as e:
        logger.error(f"Error in subscription: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe user from stock recommendations"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_active = False
            db.session.commit()
            return jsonify({'message': 'Unsubscribed successfully'}), 200
        else:
            return jsonify({'error': 'Email not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in unsubscription: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/news', methods=['GET'])
def get_news():
    """Get latest market news"""
    try:
        limit = request.args.get('limit', 10, type=int)
        news = news_service.get_latest_news(limit=limit)
        response = jsonify({'news': news})
        # Prevent CDN/browser caching so updates are visible immediately
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500

@api_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get stock recommendations"""
    try:
        symbol = request.args.get('symbol')
        if symbol:
            recommendations = recommendation_service.get_recommendations_for_symbol(symbol)
        else:
            recommendations = recommendation_service.get_latest_recommendations()
        
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        return jsonify({'error': 'Failed to fetch recommendations'}), 500

@api_bp.route('/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Get stock data and recommendation for a specific symbol"""
    try:
        stock_data = stock_service.get_stock_data(symbol)
        recommendation = recommendation_service.get_recommendation_for_symbol(symbol)
        
        return jsonify({
            'symbol': symbol,
            'stock_data': stock_data,
            'recommendation': recommendation
        })
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'stock-recommendation-api'})

@api_bp.route('/cron/eod-scan', methods=['POST'])
def cron_eod_scan():
    """Secure endpoint to run end-of-day scan and email subscribers."""
    try:
        if request.headers.get('X-CRON-SECRET') != os.getenv('CRON_SECRET'):
            return jsonify({'error': 'Unauthorized'}), 401

        symbol_universe = load_symbol_universe()
        scanned = []
        for symbol in symbol_universe:
            try:
                recommendation_service.get_recommendation_for_symbol(symbol)
                scanned.append(symbol)
            except Exception as e:
                logger.warning(f"EOD scan failed for {symbol}: {e}")

        # Send batched daily recommendations email
        try:
            email_service.send_daily_recommendations()
        except Exception as e:
            logger.warning(f"EOD email sending failed: {e}")

        return jsonify({'ok': True, 'scanned_count': len(scanned)}), 200
    except Exception as e:
        logger.error(f"Error in EOD cron: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/cron/refresh-news', methods=['POST'])
def cron_refresh_news():
    """Secure endpoint to refresh market news cache."""
    try:
        if request.headers.get('X-CRON-SECRET') != os.getenv('CRON_SECRET'):
            return jsonify({'error': 'Unauthorized'}), 401

        # Pull a larger batch to refresh cache
        _ = news_service.get_latest_news(limit=25)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f"Error in news cron: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/cron/ml-screener', methods=['POST'])
def cron_ml_screener():
    # Secure with cron secret
    cron_secret = os.getenv('CRON_SECRET')
    if request.headers.get('X-CRON-SECRET') != cron_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    results = screen_stocks()[:5]  # Get top 5 matches
    return jsonify({'ok': True, 'count': len(results), 'matches': results})

