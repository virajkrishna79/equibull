import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens or headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    let message = 'An error occurred';
    
    if (error.response) {
      // Server responded with error status
      const { data, status } = error.response;
      message = data?.error || data?.message || `Request failed with status ${status}`;
    } else if (error.request) {
      // Request was made but no response received
      message = 'No response from server. Please check your connection.';
    } else {
      // Something else happened
      message = error.message || 'Request failed';
    }
    
    // Create a new error with the formatted message
    const formattedError = new Error(message);
    formattedError.originalError = error;
    
    return Promise.reject(formattedError);
  }
);

// API functions
export const fetchNews = async (limit = 10) => {
  try {
    const response = await api.get(`/api/news?limit=${limit}`);
    return response.news || [];
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
};

export const subscribeToNewsletter = async (email) => {
  try {
    const response = await api.post('/api/subscribe', { email });
    return response;
  } catch (error) {
    console.error('Error subscribing to newsletter:', error);
    throw error;
  }
};

export const unsubscribeFromNewsletter = async (email) => {
  try {
    const response = await api.post('/api/unsubscribe', { email });
    return response;
  } catch (error) {
    console.error('Error unsubscribing from newsletter:', error);
    throw error;
  }
};

export const fetchStockData = async (symbol) => {
  try {
    const response = await api.get(`/api/stock/${symbol.toUpperCase()}`);
    return response;
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
};

export const fetchStockRecommendations = async (symbol = null) => {
  try {
    const url = symbol ? `/api/recommendations?symbol=${symbol.toUpperCase()}` : '/api/recommendations';
    const response = await api.get(url);
    return response.recommendations || [];
  } catch (error) {
    console.error('Error fetching stock recommendations:', error);
    throw error;
  }
};

export const checkApiHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return response.status === 'healthy';
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

// Utility function to format API errors
export const formatApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response;
    switch (status) {
      case 400:
        return data?.error || 'Bad request. Please check your input.';
      case 401:
        return 'Unauthorized. Please log in again.';
      case 403:
        return 'Access forbidden. You don\'t have permission for this action.';
      case 404:
        return 'Resource not found.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Internal server error. Please try again later.';
      default:
        return data?.error || `Request failed with status ${status}`;
    }
  } else if (error.request) {
    return 'No response from server. Please check your connection.';
  } else {
    return error.message || 'An unexpected error occurred.';
  }
};

export default api;
