// frontend/src/components/OAuth/AccountLinkingForm.jsx

import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './AccountLinkingForm.css';

const AccountLinkingForm = ({ onLinkSuccess, onLinkError }) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Get linking data from navigation state or URL params
  const linkingData = location.state?.linkingData || {
    email: new URLSearchParams(location.search).get('email'),
    linkToken: new URLSearchParams(location.search).get('link_token'),
    userId: new URLSearchParams(location.search).get('user_id'),
    message: new URLSearchParams(location.search).get('message')
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!password.trim()) {
      setError('Password is required');
      return;
    }

    if (!linkingData.linkToken) {
      setError('Invalid linking session. Please try signing in again.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_BASE_URL}/oauth/google/link-account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          link_token: linkingData.linkToken,
          password: password
        })
      });

      const result = await response.json();

      if (response.ok) {
        // Account linking successful
        if (result.access_token) {
          localStorage.setItem('token', result.access_token);
        }

        if (onLinkSuccess) {
          onLinkSuccess(result);
        }

        // Redirect to dashboard or original location
        const returnPath = localStorage.getItem('oauth_return_path') || '/dashboard';
        localStorage.removeItem('oauth_return_path');
        navigate(returnPath, { replace: true });

      } else {
        // Account linking failed
        const errorMessage = result.detail || 'Failed to link accounts';
        setError(errorMessage);

        if (onLinkError) {
          onLinkError({
            error: 'link_failed',
            message: errorMessage,
            status_code: response.status
          });
        }
      }

    } catch (error) {
      console.error('Account linking error:', error);
      const errorMessage = 'Network error. Please check your connection and try again.';
      setError(errorMessage);

      if (onLinkError) {
        onLinkError({
          error: 'network_error',
          message: errorMessage
        });
      }

    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    localStorage.removeItem('oauth_return_path');
    navigate('/', { replace: true });
  };

  if (!linkingData.email || !linkingData.linkToken) {
    return (
      <div className="account-linking">
        <div className="account-linking__container">
          <div className="account-linking__content">
            <div className="account-linking__icon account-linking__icon--error">
              <svg viewBox="0 0 24 24" width="48" height="48">
                <path
                  fill="#F44336"
                  d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
                />
              </svg>
            </div>
            <h2 className="account-linking__title">Invalid Linking Session</h2>
            <p className="account-linking__message">
              The account linking session has expired or is invalid. Please try signing in with Google again.
            </p>
            <button
              onClick={() => navigate('/', { replace: true })}
              className="account-linking__button account-linking__button--primary"
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="account-linking">
      <div className="account-linking__container">
        <div className="account-linking__content">
          <div className="account-linking__header">
            <div className="account-linking__icon account-linking__icon--warning">
              <svg viewBox="0 0 24 24" width="48" height="48">
                <path
                  fill="#FF9800"
                  d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
                />
              </svg>
            </div>
            <h2 className="account-linking__title">Link Your Google Account</h2>
            <p className="account-linking__subtitle">
              An account with email <strong>{linkingData.email}</strong> already exists.
            </p>
            <p className="account-linking__message">
              To link your Google account, please verify your password for the existing account.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="account-linking__form">
            <div className="account-linking__field">
              <label htmlFor="email" className="account-linking__label">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={linkingData.email}
                disabled
                className="account-linking__input account-linking__input--disabled"
              />
            </div>

            <div className="account-linking__field">
              <label htmlFor="password" className="account-linking__label">
                Password
              </label>
              <div className="account-linking__password-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="account-linking__input"
                  placeholder="Enter your current password"
                  disabled={isLoading}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="account-linking__password-toggle"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M12 17.5c-4.96 0-9-3.14-9-7s4.04-7 9-7 9 3.14 9 7-4.04 7-9 7zm0-12c-3.86 0-7 2.36-7 5s3.14 5 7 5 7-2.36 7-5-3.14-5-7-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm0-4c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z"/>
                      <path fill="currentColor" d="M2 2l20 20-1.41 1.41L2 2z"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M12 4.5C7.04 4.5 3 7.64 3 11.5s4.04 7 9 7 9-3.14 9-7-4.04-7-9-7zm0 12c-3.86 0-7-2.36-7-5s3.14-5 7-5 7 2.36 7 5-3.14 5-7 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3zm0 4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="account-linking__error">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="#F44336" d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>
                {error}
              </div>
            )}

            <div className="account-linking__actions">
              <button
                type="button"
                onClick={handleCancel}
                className="account-linking__button account-linking__button--secondary"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="account-linking__button account-linking__button--primary"
                disabled={isLoading || !password.trim()}
              >
                {isLoading ? (
                  <>
                    <div className="account-linking__spinner">
                      <div className="spinner"></div>
                    </div>
                    Linking...
                  </>
                ) : (
                  'Link Account'
                )}
              </button>
            </div>
          </form>

          <div className="account-linking__help">
            <p>
              <strong>Why am I seeing this?</strong><br />
              You tried to sign in with Google, but we found an existing account with the same email address.
              To keep your data secure, we need to verify that you own both accounts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountLinkingForm;
