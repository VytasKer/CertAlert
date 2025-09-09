import { useState, useEffect } from 'react';
import { GoogleSignInButton } from './OAuth';
import './OAuthAccountManager.css';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';
const OAUTH_STATUS_URL = import.meta.env.VITE_OAUTH_STATUS_URL || `${BACKEND_BASE_URL}/oauth/status`;
const OAUTH_UNLINK_URL = import.meta.env.VITE_OAUTH_UNLINK_URL || `${BACKEND_BASE_URL}/oauth/google/unlink-account`;

export default function OAuthAccountManager({ user, onUserUpdate }) {
  const [oauthStatus, setOauthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [unlinkLoading, setUnlinkLoading] = useState(false);

  // Fetch OAuth account status
  useEffect(() => {
    fetchOAuthStatus();
  }, []);

  const fetchOAuthStatus = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('certalert_jwt');
      if (!token) {
        setError('Please log in to view OAuth accounts');
        return;
      }

      const response = await fetch(OAUTH_STATUS_URL, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch OAuth status');
      }

      const data = await response.json();
      setOauthStatus(data);
    } catch (err) {
      console.error('OAuth status fetch error:', err);
      setError(err.message || 'Failed to load OAuth accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async (data) => {
    console.log('Google OAuth success in account manager:', data);
    // Refresh OAuth status after successful linking
    await fetchOAuthStatus();
    // Trigger user data refresh in parent component
    if (onUserUpdate) {
      onUserUpdate();
    }
  };

  const handleGoogleSignInError = (error) => {
    console.error('Google OAuth error in account manager:', error);
    setError(error.message || 'Failed to link Google account');
  };

  const handleUnlinkGoogle = async () => {
    if (!window.confirm('Are you sure you want to unlink your Google account? You will still be able to log in with your email and password.')) {
      return;
    }

    try {
      setUnlinkLoading(true);
      setError('');

      const token = localStorage.getItem('certalert_jwt');
      if (!token) {
        throw new Error('Please log in to unlink accounts');
      }

      const response = await fetch(OAUTH_UNLINK_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to unlink Google account');
      }

      const data = await response.json();
      console.log('Unlink successful:', data);

      // Refresh OAuth status after unlinking
      await fetchOAuthStatus();
      // Trigger user data refresh in parent component
      if (onUserUpdate) {
        onUserUpdate();
      }

      // Show success message
      alert('Google account unlinked successfully');
    } catch (err) {
      console.error('Unlink error:', err);
      setError(err.message || 'Failed to unlink Google account');
    } finally {
      setUnlinkLoading(false);
    }
  };

  // Check if user has Google account linked based on backend response
  const hasGoogleAccount = oauthStatus?.has_google_account || false;
  const canUnlinkGoogle = oauthStatus?.can_unlink_google || false;

  if (loading) {
    return (
      <div className="oauth-manager">
        <h3>Account Connections</h3>
        <div className="oauth-loading">
          <div className="oauth-spinner"></div>
          <span>Loading account connections...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="oauth-manager">
      <h3>Account Connections</h3>
      <p className="oauth-description">
        Link your Google account for faster sign-in and account recovery.
      </p>

      {error && (
        <div className="oauth-error">
          <span className="oauth-error-icon">⚠️</span>
          <span>{error}</span>
          <button 
            onClick={() => setError('')}
            className="oauth-error-close"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      <div className="oauth-accounts">
        {/* Google Account Section */}
        <div className="oauth-account-item">
          <div className="oauth-account-header">
            <div className="oauth-provider">
              <div className="oauth-provider-icon google-icon">
                <svg width="20" height="20" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </div>
              <span className="oauth-provider-name">Google</span>
            </div>
            <div className="oauth-account-status">
              {hasGoogleAccount ? (
                <span className="oauth-status connected">
                  <span className="oauth-status-icon">✓</span>
                  Connected
                </span>
              ) : (
                <span className="oauth-status disconnected">
                  <span className="oauth-status-icon">○</span>
                  Not connected
                </span>
              )}
            </div>
          </div>

          {hasGoogleAccount ? (
            <div className="oauth-account-details">
              <div className="oauth-account-info">
                <div className="oauth-account-email">
                  {oauthStatus?.email || user?.email || 'Connected account'}
                </div>
                <div className="oauth-account-meta">
                  Provider: {oauthStatus?.auth_provider || 'Google'}
                  {oauthStatus?.last_google_sync && (
                    ` • Last sync: ${new Date(oauthStatus.last_google_sync).toLocaleDateString()}`
                  )}
                </div>
              </div>
              {canUnlinkGoogle ? (
                <button
                  onClick={handleUnlinkGoogle}
                  disabled={unlinkLoading}
                  className="oauth-unlink-button"
                >
                  {unlinkLoading ? (
                    <>
                      <span className="oauth-spinner small"></span>
                      Unlinking...
                    </>
                  ) : (
                    'Unlink Account'
                  )}
                </button>
              ) : (
                <div className="oauth-unlink-disabled">
                  <span className="oauth-info-icon">ℹ️</span>
                  <span>Set a password first to enable unlinking</span>
                </div>
              )}
            </div>
          ) : (
            <div className="oauth-link-section">
              <p className="oauth-link-description">
                Link your Google account to enable sign-in with Google and improve account security.
              </p>
              <GoogleSignInButton
                onSuccess={handleGoogleSignIn}
                onError={handleGoogleSignInError}
                buttonText="Link Google Account"
                variant="outline"
                customRedirectUri={`${window.location.origin}/oauth/success`}
              />
            </div>
          )}
        </div>

        {/* Future OAuth providers can be added here */}
        {/* 
        <div className="oauth-account-item">
          <div className="oauth-account-header">
            <div className="oauth-provider">
              <div className="oauth-provider-icon github-icon">
                GitHub icon
              </div>
              <span className="oauth-provider-name">GitHub</span>
            </div>
            <div className="oauth-account-status">
              <span className="oauth-status disconnected">
                <span className="oauth-status-icon">○</span>
                Not connected
              </span>
            </div>
          </div>
          <div className="oauth-link-section">
            <p className="oauth-link-description">
              Connect your GitHub account for additional authentication options.
            </p>
            <button className="oauth-link-button github" disabled>
              Coming Soon
            </button>
          </div>
        </div>
        */}
      </div>

      <div className="oauth-help">
        <h4>Need Help?</h4>
        <ul>
          <li>Linking accounts provides additional sign-in options</li>
          <li>You can always sign in with your email and password</li>
          <li>Unlinking won't affect your existing account access</li>
          <li>Your data remains secure and private</li>
        </ul>
      </div>
    </div>
  );
}
