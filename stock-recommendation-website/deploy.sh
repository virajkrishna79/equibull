#!/bin/bash

echo "🚀 Starting StockAI deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend deployment
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

cd ..

# Frontend deployment
echo "🎨 Setting up frontend..."
cd frontend

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install

# Build frontend for production
echo "🏗️ Building frontend..."
npm run build

cd ..

echo "✅ Deployment setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit backend/.env file with your API keys"
echo "2. Start backend: cd backend && python app.py"
echo "3. Start frontend: cd frontend && npm start"
echo ""
echo "🌐 Backend will run on: http://localhost:5000"
echo "🌐 Frontend will run on: http://localhost:3000"
echo ""
echo "🚀 For production deployment:"
echo "- Backend: cd backend && gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo "- Frontend: cd frontend && npm run build (serve build folder)"
echo ""
echo "📚 Check README.md for detailed documentation"
