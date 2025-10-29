import React from 'react';
import { TrendingUp, Brain, Shield, Zap, Users, Award } from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {import React from 'react';
import { TrendingUp, Brain, Shield, Zap, Users, Award } from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About EquiBull
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We're revolutionizing stock market analysis by combining cutting-edge AI technology with proven financial strategies
          </p>
        </div>

        {/* Mission Section */}
        <section className="mb-16">
          <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Mission</h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                To democratize access to professional-grade stock market analysis by providing individual investors with AI-powered insights that were previously only available to institutional investors.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">What We Do</h3>
                <p className="text-gray-600 mb-4">
                  EquiBull analyzes thousands of data points including technical indicators, market sentiment, news analysis, and price patterns to generate intelligent stock recommendations.
                </p>
                <p className="text-gray-600">
                  Our system continuously learns and adapts to market conditions, ensuring our recommendations remain relevant and accurate.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Why It Matters</h3>
                <p className="text-gray-600 mb-4">
                  Individual investors often lack access to the sophisticated analysis tools used by professional traders and institutional investors.
                </p>
                <p className="text-gray-600">
                  EquiBull levels the playing field by providing retail investors with institutional-quality analysis and recommendations.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">What Makes Us Unique</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-600">
                Advanced machine learning algorithms analyze market data and sentiment to identify patterns invisible to human analysts
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-success-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Risk Management</h3>
              <p className="text-gray-600">
                Built-in risk assessment and portfolio diversification recommendations to help protect your investments
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-warning-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-Time Updates</h3>
              <p className="text-gray-600">
                Continuous monitoring of market conditions with instant alerts when opportunities arise
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Technical Analysis</h3>
              <p className="text-gray-600">
                Comprehensive technical indicators including RSI, MACD, moving averages, and volume analysis
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Community Driven</h3>
              <p className="text-gray-600">
                Learn from other investors and share insights in our growing community of smart investors
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Proven Results</h3>
              <p className="text-gray-600">
                Our recommendations have consistently outperformed market averages across various market conditions
              </p>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="mb-16">
          <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Technology Stack</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Backend & AI</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Python Flask for robust API development</li>
                  <li>• FinBERT for financial sentiment analysis</li>
                  <li>• LSTM neural networks for price prediction</li>
                  <li>• SQLAlchemy for database management</li>
                  <li>• Upstox API for real-time market data</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Frontend & UI</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• React.js for dynamic user interface</li>
                  <li>• Tailwind CSS for modern styling</li>
                  <li>• Chart.js for data visualization</li>
                  <li>• Framer Motion for smooth animations</li>
                  <li>• Responsive design for all devices</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="mb-16">
          <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Our Team</h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">AI</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Research Team</h3>
                <p className="text-gray-600">
                  Experts in machine learning and financial modeling who continuously improve our algorithms
                </p>
              </div>

              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-success-400 to-success-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">DEV</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Development Team</h3>
                <p className="text-gray-600">
                  Full-stack developers building robust, scalable systems for reliable service delivery
                </p>
              </div>

              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-warning-400 to-warning-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">FIN</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Financial Experts</h3>
                <p className="text-gray-600">
                  Seasoned financial analysts who validate and refine our investment strategies
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center">
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl shadow-lg p-8 md:p-12 text-white">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join thousands of investors who are already making smarter decisions with EquiBull
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/analysis"
                className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Start Analyzing
              </a>
              <a
                href="/"
                className="border-2 border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 rounded-lg font-semibold text-lg transition-colors duration-200"
              >
                Learn More
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;
