import React from 'react';
import { ExternalLink, Calendar, Clock } from 'lucide-react';

const NewsCard = ({ article }) => {
  const { title, description, url, source, published_at, sentiment_score, sentiment_label } = article;

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return 'Unknown date';
    }
  };

  const formatTime = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Unknown time';
    }
  };

  const getSentimentColor = (label) => {
    switch (label) {
      case 'positive':
        return 'text-success-600 bg-success-100';
      case 'negative':
        return 'text-danger-600 bg-danger-100';
      case 'neutral':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentIcon = (label) => {
    switch (label) {
      case 'positive':
        return '📈';
      case 'negative':
        return '📉';
      case 'neutral':
        return '➡️';
      default:
        return '➡️';
    }
  };

  const truncateText = (text, maxLength = 120) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="news-card group">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-medium text-gray-500">{source}</span>
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(sentiment_label)}`}>
            <span className="mr-1">{getSentimentIcon(sentiment_label)}</span>
            {sentiment_label}
          </span>
        </div>
        {sentiment_score !== null && (
          <span className="text-xs text-gray-500">
            Score: {sentiment_score.toFixed(2)}
          </span>
        )}
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors duration-200">
        {title}
      </h3>

      {description && (
        <p className="text-gray-600 mb-4 leading-relaxed">
          {truncateText(description)}
        </p>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(published_at)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{formatTime(published_at)}</span>
          </div>
        </div>

        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors duration-200"
          >
            <span>Read More</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
};

export default NewsCard;
