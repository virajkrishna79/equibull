import React, { useEffect, useState } from 'react';
import NewsCard from '../components/NewsCard';
import { fetchNews } from '../services/api';
import toast from 'react-hot-toast';

const NewsPage = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatedAt, setUpdatedAt] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await fetchNews(20);
        setNews(data);
        setUpdatedAt(new Date());
      } catch (err) {
        toast.error('Failed to load news');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="min-h-screen bg-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-baseline justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">All News</h1>
          {updatedAt && (
            <p className="text-sm text-gray-500">Updated {updatedAt.toLocaleString()}</p>
          )}
        </div>
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="news-card animate-pulse">
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
            {news.map((article, idx) => (
              <NewsCard key={idx} article={article} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsPage;
