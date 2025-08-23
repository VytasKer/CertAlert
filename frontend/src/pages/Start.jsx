import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import CertTable from '../components/CertTable';
import Welcome from '../components/Welcome';
import Footer from '../components/Footer';
import FloatingInfoBadge from '../components/FloatingInfoBadge';
import UploadModal from '../components/UploadModal';
import AuthModal from '../components/AuthModal';

export default function Start() {
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
      <Footer />
      <FloatingInfoBadge />
      {showUpload && <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />}
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </div>
  );
}