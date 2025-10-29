# StockAI - AI-Powered Stock Recommendation System

A comprehensive stock recommendation website that combines proprietary algorithms, machine learning, and real-time market data to provide intelligent investment insights.

## 🚀 Features

### Core Functionality
- **AI-Powered Stock Analysis**: Proprietary algorithm combining technical indicators, market sentiment, and ML predictions
- **Real-Time Data**: Live stock data from Upstox API with Yahoo Finance fallback
- **Machine Learning Integration**: FinBERT for sentiment analysis and LSTM for price prediction
- **Technical Indicators**: RSI, MACD, Moving Averages, Volume Analysis
- **Market Sentiment**: AI-powered news sentiment analysis

### User Experience
- **Daily Email Recommendations**: Personalized stock insights delivered to your inbox
- **Interactive Stock Analysis**: Search any stock symbol for comprehensive analysis
- **Market News**: Latest financial news with sentiment scoring
- **Responsive Design**: Mobile-first design that works on all devices
- **Real-Time Updates**: Live data and instant recommendations

### Advanced Analytics
- **Confidence Scoring**: AI-generated confidence levels for each recommendation
- **Risk Assessment**: Built-in risk management and portfolio diversification
- **Historical Analysis**: Track recommendation performance over time
- **Multi-Source Data**: Combines technical, fundamental, and sentiment data

## 🏗️ Architecture

### Backend (Python Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **APIs**: RESTful API with comprehensive endpoints
- **Services**: Modular service architecture for scalability
- **ML Models**: FinBERT sentiment analysis, LSTM price prediction

### Frontend (React.js)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS with custom components
- **Charts**: Chart.js for data visualization
- **State Management**: React hooks and context
- **Routing**: React Router for SPA navigation

### Data Sources
- **Stock Data**: Upstox API (primary), Yahoo Finance (fallback)
- **News**: NewsAPI.org for market news
- **Sentiment**: FinBERT model for financial text analysis
- **Technical Analysis**: Custom algorithms and indicators

## 🛠️ Technology Stack

### Backend Technologies
- Python 3.8+
- Flask 2.3.3
- SQLAlchemy 3.0.5
- Transformers (FinBERT)
- PyTorch
- Pandas, NumPy
- APScheduler

### Frontend Technologies
- React 18.2.0
- Tailwind CSS 3.2.7
- Chart.js 4.2.1
- Framer Motion
- Lucide React Icons
- Axios for API calls

### DevOps & Deployment
- Gunicorn (production server)
- Environment-based configuration
- Docker support (coming soon)
- CI/CD ready

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys and configuration

# Initialize database
python app.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///stock_recommendations.db

# API Keys
UPSTOX_API_KEY=your-upstox-api-key-here
NEWS_API_KEY=your-newsapi-key-here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FROM_NAME=Stock Recommendation System

# ML Model Configuration
MODEL_CACHE_DIR=./ml_models/cache
SENTIMENT_MODEL=ProsusAI/finbert
PRICE_PREDICTION_MODEL=./ml_models/price_predictor.pkl
```

## 🚀 Quick Start

### Development Mode
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### Production Deployment
```bash
# Backend
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend
cd frontend
npm run build
# Serve the build folder with your web server
```

## 📊 API Endpoints

### Main Routes
- `GET /` - Homepage with news and subscription form
- `GET /about` - About page with project information
- `GET /analysis` - Stock analysis page

### API Endpoints
- `POST /api/subscribe` - Subscribe to email recommendations
- `POST /api/unsubscribe` - Unsubscribe from recommendations
- `GET /api/news` - Get latest market news
- `GET /api/recommendations` - Get stock recommendations
- `GET /api/stock/<symbol>` - Get stock data and analysis
- `GET /api/health` - Health check endpoint

## 🤖 Machine Learning Features

### Sentiment Analysis
- **Model**: FinBERT (Financial BERT)
- **Purpose**: Analyze news and social media sentiment
- **Fallback**: Keyword-based sentiment analysis
- **Output**: Sentiment score (-1 to 1) and label

### Price Prediction
- **Model**: LSTM Neural Networks
- **Purpose**: Predict stock prices for next 5-30 days
- **Fallback**: Statistical methods (moving averages, volatility)
- **Output**: Price prediction with confidence score

### Custom Algorithm
- **Technical Indicators**: RSI, MACD, Moving Averages
- **Volume Analysis**: Trading volume patterns
- **Momentum Analysis**: Price and volume momentum
- **Risk Scoring**: Comprehensive risk assessment

## 📈 Stock Analysis Features

### Technical Indicators
- **RSI (Relative Strength Index)**: Overbought/oversold conditions
- **MACD**: Trend following momentum indicator
- **Moving Averages**: SMA 20, SMA 50 for trend analysis
- **Volume Analysis**: Trading volume patterns and trends

### Market Sentiment
- **News Analysis**: Financial news sentiment scoring
- **Social Media**: Social sentiment integration (coming soon)
- **Economic Indicators**: Market-wide sentiment analysis

### Risk Management
- **Confidence Scoring**: AI-generated confidence levels
- **Risk Assessment**: Comprehensive risk evaluation
- **Portfolio Diversification**: Multi-stock recommendations

## 🔧 Configuration

### Database Configuration
- **Development**: SQLite for easy setup
- **Production**: PostgreSQL for scalability
- **Migrations**: Automatic schema creation

### Email Configuration
- **SMTP Server**: Gmail, Outlook, or custom SMTP
- **Templates**: HTML email templates with branding
- **Scheduling**: Daily recommendation emails

### API Rate Limits
- **Upstox API**: Respect rate limits
- **News API**: Handle API quotas
- **Fallback Systems**: Graceful degradation

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test stock analysis
curl http://localhost:5000/api/stock/RELIANCE
```

## 📱 Mobile & Responsiveness

- **Mobile-First Design**: Optimized for mobile devices
- **Progressive Web App**: Installable on mobile devices
- **Touch-Friendly**: Optimized touch interactions
- **Responsive Charts**: Charts adapt to screen size

## 🔒 Security Features

- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **CORS Configuration**: Proper cross-origin setup
- **Environment Variables**: Secure configuration management
- **Rate Limiting**: API abuse prevention

## 🚀 Deployment

### Heroku Deployment
```bash
# Backend
heroku create stockai-backend
git push heroku main

# Frontend
npm run build
# Deploy build folder to static hosting
```

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Manual Deployment
```bash
# Backend
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend
cd frontend
npm run build
# Copy build folder to web server
```

## 📊 Performance Optimization

- **Database Indexing**: Optimized database queries
- **Caching**: Redis caching for frequently accessed data
- **API Optimization**: Efficient API response handling
- **Frontend Optimization**: Code splitting and lazy loading
- **Image Optimization**: Compressed and optimized assets

## 🔮 Future Enhancements

### Planned Features
- **Portfolio Management**: Track multiple stocks
- **Advanced Charts**: Interactive technical analysis charts
- **Social Features**: User communities and sharing
- **Mobile App**: Native iOS/Android applications
- **API Marketplace**: Third-party integrations

### Technical Improvements
- **Microservices**: Break down into microservices
- **Real-time Updates**: WebSocket for live data
- **Advanced ML**: More sophisticated prediction models
- **Blockchain Integration**: Crypto analysis (coming soon)

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests
- Update documentation
- Follow commit message conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FinBERT**: Financial sentiment analysis model
- **Upstox**: Real-time stock data API
- **NewsAPI**: Market news data
- **Open Source Community**: All the amazing libraries and tools

## 📞 Support

- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Email**: support@stockai.com

## 🏆 Project Status

- **Current Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: August 2024
- **Maintainers**: StockAI Team

---

**Made with ❤️ by the StockAI Team**

*Empowering investors with AI-driven insights*
