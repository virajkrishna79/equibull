import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Mail, ArrowRight, ExternalLink, Calendar, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import NewsCard from '../components/NewsCard';
import EmailSubscriptionForm from '../components/EmailSubscriptionForm';
import { fetchNews } from '../services/api';

const HomePage = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSubscribed, setIsSubscribed] = useState(false);

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    try {
      setLoading(true);
      const newsData = await fetchNews(10);
      setNews(newsData);
    } catch (error) {
      console.error('Error loading news:', error);
      toast.error('Failed to load market news');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscriptionSuccess = () => {
    setIsSubscribed(true);
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="gradient-primary text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
            AI-Powered Stock Recommendations
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
            Get intelligent stock insights powered by machine learning, technical analysis, and market sentiment
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/analysis"
              className="btn-outline bg-white text-primary-600 hover:bg-primary-50 px-8 py-3 text-lg font-semibold"
            >
              Analyze Stocks
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <button className="btn-secondary px-8 py-3 text-lg font-semibold">
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose StockAI?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our advanced system combines multiple data sources and AI algorithms to provide you with the most accurate stock recommendations
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Proprietary Algorithm</h3>
              <p className="text-gray-600">
                Our custom algorithm analyzes technical indicators, price patterns, and market momentum
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-success-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Daily Recommendations</h3>
              <p className="text-gray-600">
                Receive personalized stock recommendations directly to your email inbox
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-warning-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Market Sentiment</h3>
              <p className="text-gray-600">
                AI-powered sentiment analysis of news and social media for market insights
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Email Subscription Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Get Daily Stock Recommendations
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Subscribe to receive AI-powered stock recommendations, market analysis, and investment insights delivered to your inbox
          </p>
          <EmailSubscriptionForm onSuccess={handleSubscriptionSuccess} />
        </div>
      </section>

      {/* Market News Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Latest Market News</h2>
            <Link
              to="/news"
              className="text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
            >
              <span>View All News</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, index) => (
                <div key={index} className="news-card animate-pulse">
                  <div className="skeleton-title mb-3"></div>
                  <div className="skeleton-text mb-2"></div>
                  <div className="skeleton-text mb-2"></div>
                  <div className="skeleton-text mb-4"></div>
                  <div className="flex justify-between">
                    <div className="skeleton-text w-20"></div>
                    <div className="skeleton-text w-24"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {news.map((article, index) => (
                <NewsCard key={index} article={article} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Make Smarter Investment Decisions?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of investors who trust StockAI for their daily stock analysis and recommendations
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/analysis"
              className="btn-primary px-8 py-3 text-lg font-semibold"
            >
              Start Analyzing
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link
              to="/about"
              className="btn-outline border-white text-white hover:bg-white hover:text-gray-900 px-8 py-3 text-lg font-semibold"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
