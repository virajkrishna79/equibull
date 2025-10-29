import React, { useState } from 'react';
import { Mail, CheckCircle } from 'lucide-react';
import { subscribeToNewsletter } from '../services/api';
import toast from 'react-hot-toast';

const EmailSubscriptionForm = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isValidEmail(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await subscribeToNewsletter(email);
      setIsSubmitted(true);
      setEmail('');
      toast.success('Successfully subscribed to stock recommendations!');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      toast.error(error.message || 'Failed to subscribe. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  if (isSubmitted) {
    return (
      <div className="bg-success-50 border border-success-200 rounded-lg p-6 max-w-md mx-auto">
        <div className="flex items-center justify-center space-x-3 text-success-800">
          <CheckCircle className="w-6 h-6" />
          <span className="text-lg font-medium">Subscription Successful!</span>
        </div>
        <p className="text-success-700 text-center mt-2">
          You'll start receiving stock recommendations soon!
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field pl-10"
              placeholder="Enter your email address"
              required
              disabled={isSubmitting}
            />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting || !email.trim()}
          className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <div className="spinner"></div>
              <span>Subscribing...</span>
            </>
          ) : (
            <>
              <Mail className="w-4 h-4" />
              <span>Subscribe to Recommendations</span>
            </>
          )}
        </button>
      </form>
      
      <p className="text-sm text-gray-500 text-center mt-4">
        We respect your privacy. Unsubscribe at any time.
      </p>
    </div>
  );
};

export default EmailSubscriptionForm;
