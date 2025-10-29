import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models import StockRecommendation
from app import db
from services.stock_service import StockService
from services.news_service import NewsService
from ml_models.sentiment_analyzer import SentimentAnalyzer
from ml_models.price_predictor import PricePredictor
from ml_models.pattern_detector import PatternDetector

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.stock_service = StockService()
        self.news_service = NewsService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.price_predictor = PricePredictor()
        self.pattern_detector = PatternDetector()
        
    def get_recommendation_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Generate comprehensive recommendation for a stock symbol"""
        try:
            # Get stock data
            stock_data = self.stock_service.get_stock_data(symbol)
            technical_indicators = self.stock_service.calculate_technical_indicators(symbol)
            
            # Get news and sentiment
            news = self.news_service.get_news_for_symbol(symbol, limit=10)
            market_sentiment = self._calculate_market_sentiment(news)
            
            # Run custom algorithm
            algorithm_rec = self._run_custom_algorithm(stock_data, technical_indicators)
            
            # Get ML price prediction
            price_prediction = self.price_predictor.predict_price(symbol)
            
            # Combine algorithm with sentiment and ML
            final_recommendation = self._combine_recommendations(
                algorithm_rec, market_sentiment, price_prediction
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                algorithm_rec, market_sentiment, price_prediction
            )
            
            # Store recommendation
            recommendation = StockRecommendation(
                symbol=symbol,
                recommendation=final_recommendation['action'],
                confidence_score=confidence_score,
                algorithm_recommendation=algorithm_rec['action'],
                sentiment_score=market_sentiment['score'],
                current_price=stock_data.get('current_price', 0),
                target_price=price_prediction.get('target_price', 0),
                reasoning=final_recommendation['reasoning']
            )
            
            try:
                db.session.add(recommendation)
                db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to store recommendation: {e}")
                db.session.rollback()
            
            return {
                'symbol': symbol,
                'recommendation': final_recommendation['action'],
                'confidence_score': confidence_score,
                'algorithm_recommendation': algorithm_rec['action'],
                'sentiment_score': market_sentiment['score'],
                'current_price': stock_data.get('current_price', 0),
                'target_price': price_prediction.get('target_price', 0),
                'reasoning': final_recommendation['reasoning'],
                'technical_indicators': technical_indicators,
                'news_sentiment': market_sentiment,
                'price_prediction': price_prediction
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {symbol}: {e}")
            return self._get_default_recommendation(symbol)
    
    def _run_custom_algorithm(self, stock_data: Dict[str, Any], technical_indicators: Dict[str, float]) -> Dict[str, Any]:
        """Run custom stock recommendation algorithm"""
        try:
            current_price = stock_data.get('current_price', 0)
            change_percent = stock_data.get('change_percent', 0)
            volume = stock_data.get('volume', 0)
            
            rsi = technical_indicators.get('rsi', 50)
            sma_20 = technical_indicators.get('sma_20', 0)
            sma_50 = technical_indicators.get('sma_50', 0)
            macd = technical_indicators.get('macd', 0)
            macd_signal = technical_indicators.get('macd_signal', 0)
            
            # Initialize scoring
            score = 0
            reasons = []
            
            # Price momentum analysis
            if change_percent > 2:
                score += 2
                reasons.append("Strong positive momentum")
            elif change_percent > 0:
                score += 1
                reasons.append("Positive momentum")
            elif change_percent < -2:
                score -= 2
                reasons.append("Strong negative momentum")
            elif change_percent < 0:
                score -= 1
                reasons.append("Negative momentum")
            
            # RSI analysis
            if rsi < 30:
                score += 2
                reasons.append("Oversold condition (RSI < 30)")
            elif rsi > 70:
                score -= 2
                reasons.append("Overbought condition (RSI > 70)")
            elif 40 <= rsi <= 60:
                score += 1
                reasons.append("Neutral RSI range")
            
            # Moving average analysis
            if sma_20 > sma_50 and current_price > sma_20:
                score += 2
                reasons.append("Price above both moving averages")
            elif current_price < sma_20 and current_price < sma_50:
                score -= 2
                reasons.append("Price below both moving averages")
            
            # MACD analysis
            if macd > macd_signal:
                score += 1
                reasons.append("MACD above signal line")
            else:
                score -= 1
                reasons.append("MACD below signal line")
            
            # Volume analysis
            if volume > 1000000:  # High volume threshold
                score += 1
                reasons.append("High trading volume")
            
            # Pattern detection (from image-based algorithm - scaffold)
            try:
                hist_df = self.stock_service.get_historical_data(stock_data.get('symbol', ''), days=240)
                pattern = self.pattern_detector.detect_pattern(hist_df)
                if pattern.get('matched'):
                    score += 2
                    reasons.append(f"Pattern match: {pattern.get('details', '')}")
            except Exception:
                pass

            # Determine action based on score
            if score >= 3:
                action = "BUY"
            elif score <= -3:
                action = "SELL"
            else:
                action = "HOLD"
            
            return {
                'action': action,
                'score': score,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error in custom algorithm: {e}")
            return {
                'action': 'HOLD',
                'score': 0,
                'reasons': ['Algorithm error - defaulting to HOLD']
            }
    
    def _calculate_market_sentiment(self, news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall market sentiment from news"""
        try:
            if not news:
                return {'score': 0, 'label': 'neutral', 'count': 0}
            
            total_score = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for article in news:
                sentiment_score = article.get('sentiment_score', 0)
                sentiment_label = article.get('sentiment_label', 'neutral')
                
                total_score += sentiment_score
                
                if sentiment_label == 'positive':
                    positive_count += 1
                elif sentiment_label == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            avg_score = total_score / len(news)
            
            # Determine overall label
            if avg_score > 0.2:
                overall_label = 'positive'
            elif avg_score < -0.2:
                overall_label = 'negative'
            else:
                overall_label = 'neutral'
            
            return {
                'score': avg_score,
                'label': overall_label,
                'count': len(news),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count
            }
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return {'score': 0, 'label': 'neutral', 'count': 0}
    
    def _combine_recommendations(self, algorithm_rec: Dict[str, Any], 
                                market_sentiment: Dict[str, Any], 
                                price_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Combine algorithm recommendation with sentiment and ML predictions"""
        try:
            algorithm_action = algorithm_rec['action']
            sentiment_score = market_sentiment['score']
            sentiment_label = market_sentiment['label']
            
            # Base reasoning
            reasoning = f"Algorithm: {algorithm_action} - {', '.join(algorithm_rec['reasons'])}"
            
            # Adjust based on sentiment
            if algorithm_action == "BUY" and sentiment_label == "negative":
                if sentiment_score < -0.3:
                    final_action = "HOLD"
                    reasoning += f" | Sentiment override: Negative market sentiment ({sentiment_score:.2f})"
                else:
                    final_action = "BUY"
                    reasoning += f" | Sentiment: Slightly negative but algorithm remains strong"
            elif algorithm_action == "SELL" and sentiment_label == "positive":
                if sentiment_score > 0.3:
                    final_action = "HOLD"
                    reasoning += f" | Sentiment override: Positive market sentiment ({sentiment_score:.2f})"
                else:
                    final_action = "SELL"
                    reasoning += f" | Sentiment: Slightly positive but algorithm remains strong"
            else:
                final_action = algorithm_action
                reasoning += f" | Sentiment: {sentiment_label} ({sentiment_score:.2f})"
            
            # Add ML prediction insight
            if price_prediction.get('confidence', 0) > 0.7:
                prediction_direction = price_prediction.get('direction', 'neutral')
                if prediction_direction == 'up' and final_action == "BUY":
                    reasoning += " | ML: Price prediction supports BUY"
                elif prediction_direction == 'down' and final_action == "SELL":
                    reasoning += " | ML: Price prediction supports SELL"
                elif prediction_direction == 'up' and final_action == "SELL":
                    reasoning += " | ML: Price prediction conflicts with SELL - consider HOLD"
                elif prediction_direction == 'down' and final_action == "BUY":
                    reasoning += " | ML: Price prediction conflicts with BUY - consider HOLD"
            
            return {
                'action': final_action,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error combining recommendations: {e}")
            return {
                'action': 'HOLD',
                'reasoning': 'Error in recommendation combination - defaulting to HOLD'
            }
    
    def _calculate_confidence_score(self, algorithm_rec: Dict[str, Any], 
                                   market_sentiment: Dict[str, Any], 
                                   price_prediction: Dict[str, Any]) -> float:
        """Calculate confidence score for the recommendation"""
        try:
            # Base confidence from algorithm score
            algorithm_score = abs(algorithm_rec.get('score', 0))
            base_confidence = min(algorithm_score / 5.0, 1.0) * 0.6  # Max 60% from algorithm
            
            # Sentiment confidence
            sentiment_confidence = 0.2  # Base 20%
            if market_sentiment['count'] > 0:
                sentiment_confidence += 0.1  # Bonus for having news data
            
            # ML prediction confidence
            ml_confidence = 0.0
            if price_prediction.get('confidence', 0) > 0.5:
                ml_confidence = price_prediction['confidence'] * 0.2  # Max 20% from ML
            
            total_confidence = base_confidence + sentiment_confidence + ml_confidence
            
            return min(total_confidence, 1.0)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5  # Default 50% confidence
    
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
            'reasoning': 'Unable to generate recommendation - defaulting to HOLD',
            'technical_indicators': {},
            'news_sentiment': {'score': 0, 'label': 'neutral'},
            'price_prediction': {'confidence': 0, 'direction': 'neutral'}
        }
