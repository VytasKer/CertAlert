// frontend/src/components/OAuth/OAuthCallback.jsx

import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './OAuthCallback.css';

const OAuthCallback = ({ onAuthSuccess, onAuthError, onAccountLinkingRequired }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing'); // 'processing', 'success', 'error', 'linking_required'
  const [message, setMessage] = useState('Processing OAuth authentication...');
  const [linkingData, setLinkingData] = useState(null);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        const urlParams = new URLSearchParams(location.search);
        const action = urlParams.get('action');
        const error = urlParams.get('error');

        // Handle different OAuth callback scenarios
        if (error) {
          // OAuth error occurred
          handleOAuthError({
            error: error,
            message: urlParams.get('message') || 'Authentication failed',
            status_code: urlParams.get('status_code')
          });
        } else if (action === 'link_required') {
          // Account linking required
          handleAccountLinking({
            email: urlParams.get('email'),
            linkToken: urlParams.get('link_token'),
            userId: urlParams.get('user_id'),
            message: urlParams.get('message')
          });
        } else if (action === 'login_success' || action === 'user_created') {
          // Successful OAuth authentication
          handleOAuthSuccess({
            action: action,
            token: urlParams.get('token'),
            userId: urlParams.get('user_id'),
            email: urlParams.get('email'),
            provider: urlParams.get('provider')
          });
        } else {
          // Unknown callback state
          handleOAuthError({
            error: 'unknown_callback',
            message: 'Unknown OAuth callback state'
          });
        }
      } catch (error) {
        console.error('OAuth callback processing error:', error);
        handleOAuthError({
          error: 'callback_processing_failed',
          message: 'Failed to process OAuth callback'
        });
      }
    };

    handleOAuthCallback();
  }, [location.search]);

  const handleOAuthSuccess = (data) => {
    setStatus('success');
    setMessage(
      data.action === 'user_created' 
        ? 'Account created successfully! Redirecting...'
        : 'Authentication successful! Redirecting...'
    );

    // Store authentication token
    if (data.token) {
      localStorage.setItem('token', data.token);
    }

    // Clear OAuth session data
    sessionStorage.removeItem('oauth_success_callback');
    sessionStorage.removeItem('oauth_error_callback');

    // Call success callback if provided
    if (onAuthSuccess) {
      onAuthSuccess(data);
    }

    // Redirect to original location or dashboard
    setTimeout(() => {
      const returnPath = localStorage.getItem('oauth_return_path') || '/dashboard';
      localStorage.removeItem('oauth_return_path');
      navigate(returnPath, { replace: true });
    }, 2000);
  };

  const handleOAuthError = (errorData) => {
    setStatus('error');
    setMessage(errorData.message || 'Authentication failed');

    // Clear OAuth session data
    sessionStorage.removeItem('oauth_success_callback');
    sessionStorage.removeItem('oauth_error_callback');

    // Call error callback if provided
    if (onAuthError) {
      onAuthError(errorData);
    }

    // Redirect to login after delay
    setTimeout(() => {
      localStorage.removeItem('oauth_return_path');
      navigate('/', { replace: true });
    }, 5000);
  };

  const handleAccountLinking = (data) => {
    setStatus('linking_required');
    setMessage('Account linking required');
    setLinkingData(data);

    // Call account linking callback if provided
    if (onAccountLinkingRequired) {
      onAccountLinkingRequired(data);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return (
          <div className="oauth-callback__spinner">
            <div className="spinner"></div>
          </div>
        );
      case 'success':
        return (
          <div className="oauth-callback__icon oauth-callback__icon--success">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path
                fill="#4CAF50"
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
              />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="oauth-callback__icon oauth-callback__icon--error">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path
                fill="#F44336"
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
              />
            </svg>
          </div>
        );
      case 'linking_required':
        return (
          <div className="oauth-callback__icon oauth-callback__icon--warning">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path
                fill="#FF9800"
                d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
              />
            </svg>
          </div>
        );
      default:
        return null;
    }
  };

  if (status === 'linking_required' && linkingData) {
    // Redirect to account linking page
    navigate('/oauth/link-account', { 
      state: { linkingData },
      replace: true 
    });
    return null;
  }

  return (
    <div className="oauth-callback">
      <div className="oauth-callback__container">
        <div className="oauth-callback__content">
          {getStatusIcon()}
          <h2 className="oauth-callback__title">
            {status === 'processing' && 'Processing Authentication'}
            {status === 'success' && 'Authentication Successful'}
            {status === 'error' && 'Authentication Failed'}
            {status === 'linking_required' && 'Account Linking Required'}
          </h2>
          <p className="oauth-callback__message">{message}</p>
          
          {status === 'error' && (
            <div className="oauth-callback__actions">
              <button
                onClick={() => navigate('/', { replace: true })}
                className="oauth-callback__button oauth-callback__button--primary"
              >
                Return to Home
              </button>
            </div>
          )}

          {status === 'processing' && (
            <div className="oauth-callback__progress">
              <div className="oauth-callback__progress-bar">
                <div className="oauth-callback__progress-fill"></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OAuthCallback;
