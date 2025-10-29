import logging
from typing import List, Dict, Any, Tuple
import os
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self._load_model()
        
    def _load_model(self):
        """Load the sentiment analysis model"""
        try:
            # Try to load FinBERT for financial sentiment analysis
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
                
                # Use FinBERT model specifically trained for financial text
                model_name = "ProsusAI/finbert"
                
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name
                )
                
                self.is_loaded = True
                logger.info("FinBERT model loaded successfully")
                
            except ImportError:
                logger.warning("Transformers library not available, using fallback sentiment analysis")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            self.is_loaded = False
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        try:
            if self.is_loaded and self.sentiment_pipeline:
                return self._analyze_with_finbert(text)
            else:
                return self._analyze_with_keywords(text)
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._get_neutral_sentiment()
    
    def analyze_batch_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts"""
        try:
            if self.is_loaded and self.sentiment_pipeline:
                return self._analyze_batch_with_finbert(texts)
            else:
                return [self._analyze_with_keywords(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {e}")
            return [self._get_neutral_sentiment() for _ in texts]
    
    def _analyze_with_finbert(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using FinBERT model"""
        try:
            # Truncate text if too long for model
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self.sentiment_pipeline(text)
            
            # FinBERT returns: positive, negative, neutral
            label = result[0]['label']
            score = result[0]['score']
            
            # Convert to our format
            if label == 'positive':
                sentiment_score = score
                sentiment_label = 'positive'
            elif label == 'negative':
                sentiment_score = -score
                sentiment_label = 'negative'
            else:  # neutral
                sentiment_score = 0.0
                sentiment_label = 'neutral'
            
            return {
                'text': text,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': score,
                'model': 'finbert'
            }
            
        except Exception as e:
            logger.error(f"FinBERT analysis failed: {e}")
            return self._analyze_with_keywords(text)
    
    def _analyze_batch_with_finbert(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts using FinBERT"""
        try:
            # Truncate texts if too long
            max_length = 512
            truncated_texts = [text[:max_length] if len(text) > max_length else text for text in texts]
            
            results = self.sentiment_pipeline(truncated_texts)
            
            analyzed_results = []
            for i, result in enumerate(results):
                label = result['label']
                score = result['score']
                
                if label == 'positive':
                    sentiment_score = score
                    sentiment_label = 'positive'
                elif label == 'negative':
                    sentiment_score = -score
                    sentiment_label = 'negative'
                else:  # neutral
                    sentiment_score = 0.0
                    sentiment_label = 'neutral'
                
                analyzed_results.append({
                    'text': texts[i],
                    'sentiment_score': sentiment_score,
                    'sentiment_label': sentiment_label,
                    'confidence': score,
                    'model': 'finbert'
                })
            
            return analyzed_results
            
        except Exception as e:
            logger.error(f"Batch FinBERT analysis failed: {e}")
            return [self._analyze_with_keywords(text) for text in texts]
    
    def _analyze_with_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based sentiment analysis"""
        try:
            # Financial-specific positive keywords
            positive_keywords = [
                'surge', 'jump', 'rise', 'gain', 'profit', 'earnings', 'growth',
                'positive', 'bullish', 'rally', 'breakout', 'strong', 'up', 'higher',
                'beat', 'exceed', 'outperform', 'recovery', 'bounce', 'climb'
            ]
            
            # Financial-specific negative keywords
            negative_keywords = [
                'fall', 'drop', 'decline', 'loss', 'crash', 'bearish', 'weak',
                'negative', 'down', 'plunge', 'slump', 'concern', 'risk', 'lower',
                'miss', 'disappoint', 'underperform', 'selloff', 'correction'
            ]
            
            # Financial-specific neutral keywords
            neutral_keywords = [
                'stable', 'steady', 'maintain', 'hold', 'unchanged', 'flat',
                'consolidate', 'range', 'support', 'resistance', 'technical'
            ]
            
            text_lower = text.lower()
            
            # Count keyword occurrences
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)
            neutral_count = sum(1 for word in neutral_keywords if word in text_lower)
            
            # Calculate sentiment score
            if positive_count > negative_count:
                sentiment_score = min(0.8, positive_count * 0.2)
                sentiment_label = 'positive'
                confidence = min(0.9, (positive_count / max(positive_count + negative_count, 1)) * 0.9)
            elif negative_count > positive_count:
                sentiment_score = max(-0.8, -negative_count * 0.2)
                sentiment_label = 'negative'
                confidence = min(0.9, (negative_count / max(positive_count + negative_count, 1)) * 0.9)
            else:
                sentiment_score = 0.0
                sentiment_label = 'neutral'
                confidence = 0.7
            
            return {
                'text': text,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'confidence': confidence,
                'model': 'keyword_based'
            }
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            return self._get_neutral_sentiment()
    
    def _get_neutral_sentiment(self) -> Dict[str, Any]:
        """Return neutral sentiment when analysis fails"""
        return {
            'text': '',
            'sentiment_score': 0.0,
            'sentiment_label': 'neutral',
            'confidence': 0.5,
            'model': 'fallback'
        }
    
    def get_market_sentiment_summary(self, texts: List[str]) -> Dict[str, Any]:
        """Get overall market sentiment summary from multiple texts"""
        try:
            if not texts:
                return {
                    'overall_sentiment': 'neutral',
                    'sentiment_score': 0.0,
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_texts': 0
                }
            
            # Analyze all texts
            results = self.analyze_batch_sentiment(texts)
            
            # Calculate summary statistics
            total_score = sum(result['sentiment_score'] for result in results)
            avg_score = total_score / len(results)
            
            positive_count = sum(1 for r in results if r['sentiment_label'] == 'positive')
            negative_count = sum(1 for r in results if r['sentiment_label'] == 'negative')
            neutral_count = sum(1 for r in results if r['sentiment_label'] == 'neutral')
            
            # Determine overall sentiment
            if avg_score > 0.2:
                overall_sentiment = 'positive'
            elif avg_score < -0.2:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            # Calculate confidence based on consistency
            total_confidence = sum(result['confidence'] for result in results)
            avg_confidence = total_confidence / len(results)
            
            return {
                'overall_sentiment': overall_sentiment,
                'sentiment_score': avg_score,
                'confidence': avg_confidence,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_texts': len(texts)
            }
            
        except Exception as e:
            logger.error(f"Error getting market sentiment summary: {e}")
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_texts': 0
            }
    
    def is_model_available(self) -> bool:
        """Check if the ML model is available"""
        return self.is_loaded
