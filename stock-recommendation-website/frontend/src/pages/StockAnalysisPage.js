import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Search, TrendingUp, TrendingDown, Minus, BarChart3, Info } from 'lucide-react';
import toast from 'react-hot-toast';

const StockAnalysisPage = () => {
  const { symbol } = useParams();
  const [searchSymbol, setSearchSymbol] = useState(symbol || '');
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchSymbol.trim()) {
      toast.error('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    
    try {
      // Mock API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock data for demonstration
      const mockStockData = {
        symbol: searchSymbol.toUpperCase(),
        current_price: 1250.50,
        change: 45.25,
        change_percent: 3.75,
        volume: 1250000,
        high: 1280.00,
        low: 1205.00,
        open: 1210.00,
        previous_close: 1205.25,
        source: 'upstox'
      };

      const mockRecommendation = {
        symbol: searchSymbol.toUpperCase(),
        recommendation: 'BUY',
        confidence_score: 0.85,
        algorithm_recommendation: 'BUY',
        sentiment_score: 0.6,
        current_price: 1250.50,
        target_price: 1350.00,
        reasoning: 'Strong technical indicators with positive momentum. RSI shows oversold condition, moving averages are bullish, and volume is increasing. Market sentiment is positive with recent news.',
        technical_indicators: {
          rsi: 35.2,
          sma_20: 1230.00,
          sma_50: 1180.00,
          macd: 15.5,
          macd_signal: 8.2
        },
        news_sentiment: {
          score: 0.6,
          label: 'positive',
          count: 8
        },
        price_prediction: {
          confidence: 0.78,
          direction: 'up',
          target_price: 1350.00
        }
      };

      setStockData(mockStockData);
      setRecommendation(mockRecommendation);
      
    } catch (error) {
      toast.error('Failed to fetch stock data. Please try again.');
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (rec) => {
    switch (rec) {
      case 'BUY':
        return 'text-success-600 bg-success-100';
      case 'SELL':
        return 'text-danger-600 bg-danger-100';
      case 'HOLD':
        return 'text-warning-600 bg-warning-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getRecommendationIcon = (rec) => {
    switch (rec) {
      case 'BUY':
        return <TrendingUp className="w-5 h-5" />;
      case 'SELL':
        return <TrendingDown className="w-5 h-5" />;
      case 'HOLD':
        return <Minus className="w-5 h-5" />;
      default:
        return <Minus className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Stock Analysis & Recommendations
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get AI-powered stock analysis, technical indicators, and personalized recommendations for any stock symbol
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <form onSubmit={handleSearch} className="max-w-md mx-auto">
            <div className="flex space-x-2">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchSymbol}
                  onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
                  placeholder="Enter stock symbol (e.g., RELIANCE, TCS)"
                  className="input-field w-full"
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading || !searchSymbol.trim()}
                className="btn-primary px-6 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="spinner"></div>
                ) : (
                  <Search className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {stockData && recommendation && (
          <div className="space-y-8">
            {/* Stock Overview */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
                Stock Overview - {stockData.symbol}
              </h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">₹{stockData.current_price.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Current Price</div>
                </div>
                
                <div className="text-center">
                  <div className={`text-xl font-semibold ${stockData.change >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                    {stockData.change >= 0 ? '+' : ''}₹{stockData.change.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-500">Change</div>
                </div>
                
                <div className="text-center">
                  <div className={`text-xl font-semibold ${stockData.change_percent >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                    {stockData.change_percent >= 0 ? '+' : ''}{stockData.change_percent.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-500">Change %</div>
                </div>
                
                <div className="text-center">
                  <div className="text-xl font-semibold text-gray-900">{stockData.volume.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Volume</div>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">₹{stockData.high.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Day High</div>
                </div>
                
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">₹{stockData.low.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Day Low</div>
                </div>
                
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">₹{stockData.open.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Open</div>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Info className="w-6 h-6 mr-2 text-primary-600" />
                AI Recommendation
              </h2>
              
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRecommendationColor(recommendation.recommendation)}`}>
                      {getRecommendationIcon(recommendation.recommendation)}
                      <span className="ml-2">{recommendation.recommendation}</span>
                    </span>
                    <span className="text-sm text-gray-500">
                      Confidence: {(recommendation.confidence_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Reasoning</h4>
                      <p className="text-gray-600 text-sm leading-relaxed">{recommendation.reasoning}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Target Price</h4>
                      <p className="text-lg font-semibold text-success-600">₹{recommendation.target_price.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Technical Indicators</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">RSI:</span>
                      <span className="font-medium">{recommendation.technical_indicators.rsi.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">SMA 20:</span>
                      <span className="font-medium">₹{recommendation.technical_indicators.sma_20.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">SMA 50:</span>
                      <span className="font-medium">₹{recommendation.technical_indicators.sma_50.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">MACD:</span>
                      <span className="font-medium">{recommendation.technical_indicators.macd.toFixed(1)}</span>
                    </div>
                  </div>
                  
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-2">Market Sentiment</h4>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getRecommendationColor(recommendation.news_sentiment.label)}`}>
                        {recommendation.news_sentiment.label}
                      </span>
                      <span className="text-sm text-gray-600">
                        Score: {recommendation.news_sentiment.score.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Important Disclaimer</h3>
              <p className="text-yellow-700 text-sm">
                This analysis is for informational purposes only and should not be considered as financial advice. 
                The recommendations are based on AI algorithms and historical data analysis. Always do your own research, 
                consider your risk tolerance, and consult with a financial advisor before making investment decisions. 
                Past performance does not guarantee future results.
              </p>
            </div>
          </div>
        )}

        {/* No Results State */}
        {!stockData && !loading && (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Search for a Stock</h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Enter a stock symbol above to get AI-powered analysis, technical indicators, and personalized recommendations
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockAnalysisPage;
