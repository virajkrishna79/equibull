import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import pickle
from services.stock_service import StockService

logger = logging.getLogger(__name__)

class PricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_loaded = False
        self.stock_service = StockService()
        self._load_model()
        
    def _load_model(self):
        """Load the price prediction model"""
        try:
            # Try to load pre-trained model
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'price_predictor.pkl')
            scaler_path = os.path.join(os.path.dirname(__file__), 'models', 'price_scaler.pkl')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_loaded = True
                logger.info("Price prediction model loaded successfully")
            else:
                logger.info("No pre-trained model found, using statistical prediction")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading price prediction model: {e}")
            self.is_loaded = False
    
    def predict_price(self, symbol: str, days_ahead: int = 5) -> Dict[str, Any]:
        """Predict stock price for the next N days"""
        try:
            if self.is_loaded and self.model:
                return self._predict_with_ml_model(symbol, days_ahead)
            else:
                return self._predict_with_statistics(symbol, days_ahead)
                
        except Exception as e:
            logger.error(f"Error predicting price for {symbol}: {e}")
            return self._get_default_prediction(symbol)
    
    def _predict_with_ml_model(self, symbol: str, days_ahead: int) -> Dict[str, Any]:
        """Predict using trained ML model"""
        try:
            # Get historical data
            hist_data = self.stock_service.get_historical_data(symbol, days=60)
            if hist_data.empty:
                return self._predict_with_statistics(symbol, days_ahead)
            
            # Prepare features
            features = self._prepare_features(hist_data)
            if features is None:
                return self._predict_with_statistics(symbol, days_ahead)
            
            # Make prediction
            scaled_features = self.scaler.transform(features.reshape(1, -1))
            prediction = self.model.predict(scaled_features)
            
            # Inverse transform prediction
            predicted_price = self.scaler.inverse_transform(prediction.reshape(-1, 1))[0][0]
            
            # Calculate confidence and direction
            confidence = self._calculate_ml_confidence(features)
            current_price = hist_data['Close'].iloc[-1]
            direction = 'up' if predicted_price > current_price else 'down'
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'predicted_price': predicted_price,
                'target_price': predicted_price,
                'days_ahead': days_ahead,
                'confidence': confidence,
                'direction': direction,
                'model': 'ml_lstm'
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return self._predict_with_statistics(symbol, days_ahead)
    
    def _predict_with_statistics(self, symbol: str, days_ahead: int) -> Dict[str, Any]:
        """Predict using statistical methods"""
        try:
            # Get historical data
            hist_data = self.stock_service.get_historical_data(symbol, days=30)
            if hist_data.empty:
                return self._get_default_prediction(symbol)
            
            current_price = hist_data['Close'].iloc[-1]
            
            # Calculate moving averages
            sma_5 = hist_data['Close'].rolling(window=5).mean().iloc[-1]
            sma_20 = hist_data['Close'].rolling(window=20).mean().iloc[-1]
            
            # Calculate volatility
            returns = hist_data['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # Calculate trend
            trend = (sma_5 - sma_20) / sma_20
            
            # Simple prediction based on trend and volatility
            if trend > 0.02:  # Strong upward trend
                predicted_change = 0.01 + (volatility * 0.5)  # 1% + half volatility
                direction = 'up'
            elif trend < -0.02:  # Strong downward trend
                predicted_change = -0.01 - (volatility * 0.5)  # -1% - half volatility
                direction = 'down'
            else:  # Sideways trend
                predicted_change = np.random.normal(0, volatility * 0.3)  # Random walk
                direction = 'up' if predicted_change > 0 else 'down'
            
            # Apply prediction
            predicted_price = current_price * (1 + predicted_change)
            
            # Calculate confidence based on trend strength and volatility
            trend_strength = abs(trend)
            confidence = min(0.8, 0.5 + (trend_strength * 2) - (volatility * 10))
            confidence = max(0.3, confidence)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'predicted_price': predicted_price,
                'target_price': predicted_price,
                'days_ahead': days_ahead,
                'confidence': confidence,
                'direction': direction,
                'model': 'statistical',
                'trend': trend,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Statistical prediction failed: {e}")
            return self._get_default_prediction(symbol)
    
    def _prepare_features(self, hist_data: pd.DataFrame) -> Optional[np.ndarray]:
        """Prepare features for ML model"""
        try:
            if len(hist_data) < 20:
                return None
            
            # Calculate technical indicators
            features = []
            
            # Price features
            features.extend([
                hist_data['Close'].iloc[-1],  # Current price
                hist_data['Close'].iloc[-5],  # 5 days ago
                hist_data['Close'].iloc[-10], # 10 days ago
                hist_data['Close'].iloc[-20], # 20 days ago
            ])
            
            # Moving averages
            sma_5 = hist_data['Close'].rolling(window=5).mean()
            sma_10 = hist_data['Close'].rolling(window=10).mean()
            sma_20 = hist_data['Close'].rolling(window=20).mean()
            
            features.extend([
                sma_5.iloc[-1],
                sma_10.iloc[-1],
                sma_20.iloc[-1],
                sma_5.iloc[-1] - sma_20.iloc[-1],  # MA difference
            ])
            
            # Volume features
            features.extend([
                hist_data['Volume'].iloc[-1],
                hist_data['Volume'].rolling(window=5).mean().iloc[-1],
                hist_data['Volume'].rolling(window=20).mean().iloc[-1],
            ])
            
            # Volatility features
            returns = hist_data['Close'].pct_change().dropna()
            features.extend([
                returns.std(),
                returns.rolling(window=10).std().iloc[-1],
                returns.rolling(window=20).std().iloc[-1],
            ])
            
            # RSI
            delta = hist_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            features.append(rsi.iloc[-1])
            
            # Convert to numpy array
            features = np.array(features, dtype=np.float32)
            
            # Handle NaN values
            if np.any(np.isnan(features)):
                features = np.nan_to_num(features, nan=0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def _calculate_ml_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence for ML prediction"""
        try:
            # Simple confidence calculation based on feature quality
            # In production, you might use model uncertainty or ensemble methods
            
            # Check for extreme values
            feature_std = np.std(features)
            feature_mean = np.mean(features)
            
            # Normalize features
            normalized_features = (features - feature_mean) / (feature_std + 1e-8)
            
            # Calculate confidence based on feature stability
            extreme_count = np.sum(np.abs(normalized_features) > 3)  # Count extreme values
            
            base_confidence = 0.7
            if extreme_count == 0:
                confidence = base_confidence + 0.2  # High confidence
            elif extreme_count <= 2:
                confidence = base_confidence + 0.1  # Medium confidence
            else:
                confidence = base_confidence - 0.1  # Lower confidence
            
            return min(0.9, max(0.3, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating ML confidence: {e}")
            return 0.5
    
    def _get_default_prediction(self, symbol: str) -> Dict[str, Any]:
        """Return default prediction when all methods fail"""
        return {
            'symbol': symbol,
            'current_price': 0,
            'predicted_price': 0,
            'target_price': 0,
            'days_ahead': 5,
            'confidence': 0.3,
            'direction': 'neutral',
            'model': 'default'
        }
    
    def train_model(self, symbol: str, days: int = 365) -> bool:
        """Train the price prediction model (placeholder for future implementation)"""
        try:
            logger.info(f"Training price prediction model for {symbol}")
            # This is a placeholder - in production you would:
            # 1. Collect more historical data
            # 2. Implement LSTM/GRU model training
            # 3. Save the trained model
            # 4. Update model performance metrics
            
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def get_prediction_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical predictions for a symbol"""
        try:
            # This would typically query a database of past predictions
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting prediction history: {e}")
            return []
    
    def is_model_available(self) -> bool:
        """Check if the ML model is available"""
        return self.is_loaded
