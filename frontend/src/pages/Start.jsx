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

export default function Start() {
  usePageTitle('CertAlert');
  
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  useEffect(() => {
    localStorage.removeItem('certalert_jwt');
    localStorage.removeItem('certalert_user_id');
    // Add any other session keys you use here
  }, []);
  const isLoggedIn = !!localStorage.getItem('certalert_jwt');

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
      {!isLoggedIn && (
        <div style={{ 
          textAlign: 'center', 
          margin: '2rem 0',
          padding: '1rem'
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
              style={{
                fontSize: '1.1em',
                padding: '0.8em 2em',
                fontWeight: '600',
                borderRadius: '8px',
                border: '2px solid #646cff',
                backgroundColor: '#646cff',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.25s ease',
                boxShadow: '0 4px 8px rgba(100, 108, 255, 0.2)',
                width: '100%'
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = '#646cff';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = '#646cff';
                e.target.style.color = 'white';
              }}
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