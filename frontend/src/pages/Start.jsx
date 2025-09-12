import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import CertTable from '../components/CertTable';
import Welcome from '../components/Welcome';
import Footer from '../components/Footer';
import FloatingInfoBadge from '../components/FloatingInfoBadge';
import UploadModal from '../components/UploadModal';
import AuthModal from '../components/AuthModal';
import { GoogleSignInButton } from '../components/OAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { useAuth } from '../hooks/useAuth';

export default function Start() {
  usePageTitle('CertAlert');
  
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const { isLoggedIn, isLoading, logout } = useAuth();

  useEffect(() => {
    // Clear authentication on Start page load since this is the landing page
    logout();
  }, []);

  return (
    <div className="start-page">
      <Header
        onUpload={() => {
          if (isLoggedIn) setShowUpload(true);
          else setShowAuthModal(true);
        }}
        onLogin={!isLoggedIn ? () => setShowAuthModal(true) : undefined}
      />
      <div style={{ marginTop: '2rem' }}>
        <CertTable blurred onAction={() => {
          if (isLoggedIn) setShowUpload(true);
          else setShowAuthModal(true);
        }} />
      </div>
      <Welcome />
      {!isLoading && !isLoggedIn && (
        <div style={{ 
          textAlign: 'center', 
          margin: '2rem 0',
          padding: '1rem',
          opacity: isLoading ? 0 : 1,
          transition: 'opacity 0.3s ease-in-out'
        }}>
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '1rem', 
            alignItems: 'center',
            maxWidth: '300px',
            margin: '0 auto'
          }}>
            <button 
              onClick={() => setShowAuthModal(true)}
              className="login-cta-button"
            >
              Login to Get Started
            </button>
            
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              width: '100%',
              margin: '0.5rem 0',
              color: '#6b7280',
              fontSize: '14px'
            }}>
              <div style={{ flex: 1, height: '1px', backgroundColor: '#e5e7eb' }}></div>
              <span style={{ padding: '0 16px' }}>or</span>
              <div style={{ flex: 1, height: '1px', backgroundColor: '#e5e7eb' }}></div>
            </div>
            
            <GoogleSignInButton
              onSuccess={(data) => {
                console.log('Google OAuth success from Start page:', data);
                // User will be redirected by the OAuth flow
              }}
              onError={(error) => {
                console.error('Google OAuth error from Start page:', error);
                // Could show a toast notification here
              }}
              buttonText="Continue with Google"
              variant="secondary"
            />
          </div>
        </div>
      )}
      <Footer />
      <FloatingInfoBadge />
      {showUpload && <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />}
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </div>
  );
}