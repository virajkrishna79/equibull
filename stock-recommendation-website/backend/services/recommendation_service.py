import logging
from typing import List, Dict, Any
from datetime import datetime
from models import StockRecommendation
from app import db
from ml_models.screener_scan import run_screener

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        # Only initialize what we need for screening
        pass
        
    def get_screener_recommendations(self) -> List[Dict[str, Any]]:
        """Get stock recommendations based on screener results"""
        try:
            # Run the screener to get filtered stocks
            screened_stocks = run_screener()
            
            recommendations = []
            
            for stock in screened_stocks:
                # Create recommendation based on screener criteria
                recommendation = self._create_recommendation_from_screener(stock)
                recommendations.append(recommendation)
                
                # Store in database
                try:
                    db_recommendation = StockRecommendation(
                        symbol=stock['Ticker'],
                        recommendation=recommendation['recommendation'],
                        confidence_score=recommendation['confidence_score'],
                        algorithm_recommendation=recommendation['recommendation'],
                        sentiment_score=0,  # Not using sentiment
                        current_price=stock['Price'],
                        target_price=0,  # Not using price prediction
                        reasoning=recommendation['reasoning']
                    )
                    db.session.add(db_recommendation)
                except Exception as e:
                    logger.warning(f"Failed to store recommendation for {stock['Ticker']}: {e}")
                    db.session.rollback()
            
            # Commit all recommendations
            try:
                db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to commit recommendations: {e}")
                db.session.rollback()
            
            logger.info(f"Generated {len(recommendations)} screener-based recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating screener recommendations: {e}")
            return []
    
    def _create_recommendation_from_screener(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create recommendation from screener stock data"""
        try:
            ticker = stock_data['Ticker']
            current_price = stock_data['Price']
            down_from_high = stock_data['%DownFromHigh']
            mcap = stock_data['MCap(Cr)']
            score = stock_data.get('Score', 3)  # Default score if not provided
            
            # Determine recommendation based on screener logic
            if down_from_high <= 10:  # Within 10% of 52W high - STRONG BUY
                recommendation = "BUY"
                confidence = 0.8
                reasoning = f"Strong momentum - only {down_from_high}% below 52W high | Large cap: ₹{mcap}Cr"
            elif down_from_high <= 20:  # Within 20% of 52W high - BUY
                recommendation = "BUY" 
                confidence = 0.7
                reasoning = f"Good momentum - {down_from_high}% below 52W high | Market cap: ₹{mcap}Cr"
            else:  # More than 20% below - HOLD
                recommendation = "HOLD"
                confidence = 0.6
                reasoning = f"Waiting for better entry - {down_from_high}% below 52W high | Market cap: ₹{mcap}Cr"
            
            # Adjust confidence based on screener score if available
            if 'Score' in stock_data:
                confidence = min(confidence + (stock_data['Score'] * 0.05), 0.9)
                reasoning += f" | Screener score: {stock_data['Score']}/5"
            
            return {
                'symbol': ticker,
                'recommendation': recommendation,
                'confidence_score': confidence,
                'algorithm_recommendation': recommendation,
                'sentiment_score': 0,
                'current_price': current_price,
                'target_price': 0,
                'reasoning': reasoning,
                'screener_data': stock_data
            }
            
        except Exception as e:
            logger.error(f"Error creating recommendation for {stock_data.get('Ticker', 'Unknown')}: {e}")
            return self._get_default_recommendation(stock_data.get('Ticker', 'Unknown'))
    
    def get_recommendation_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Get recommendation for a specific symbol using screener logic"""
        try:
            # Run screener for this specific symbol
            screened_stocks = run_screener()
            
            # Find the symbol in screener results
            stock_data = next(
                (stock for stock in screened_stocks if stock['Ticker'] == symbol.upper()), 
                None
            )
            
            if stock_data:
                return self._create_recommendation_from_screener(stock_data)
            else:
                # Symbol not found in screener results - not recommended
                return {
                    'symbol': symbol,
                    'recommendation': 'HOLD',
                    'confidence_score': 0.3,
                    'algorithm_recommendation': 'HOLD',
                    'sentiment_score': 0,
                    'current_price': 0,
                    'target_price': 0,
                    'reasoning': 'Stock did not pass screener filters',
                    'screener_data': None
                }
                
        except Exception as e:
            logger.error(f"Error getting recommendation for {symbol}: {e}")
            return self._get_default_recommendation(symbol)
    
    def get_latest_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest stock recommendations from database"""
        try:
            recommendations = StockRecommendation.query.order_by(
                StockRecommendation.created_at.desc()
            ).limit(limit).all()
            
            return [rec.to_dict() for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Error fetching latest recommendations: {e}")
            return []
    
    def get_recommendations_for_symbol(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommendations for a specific symbol"""
        try:
            recommendations = StockRecommendation.query.filter_by(
                symbol=symbol.upper()
            ).order_by(
                StockRecommendation.created_at.desc()
            ).limit(limit).all()
            
            return [rec.to_dict() for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Error fetching recommendations for {symbol}: {e}")
            return []
    
    def _get_default_recommendation(self, symbol: str) -> Dict[str, Any]:
        """Return default recommendation when algorithm fails"""
        return {
            'symbol': symbol,
            'recommendation': 'HOLD',
            'confidence_score': 0.3,
            'algorithm_recommendation': 'HOLD',
            'sentiment_score': 0,
            'current_price': 0,
            'target_price': 0,
            'reasoning': 'Unable to generate recommendation',
            'screener_data': None
        }
