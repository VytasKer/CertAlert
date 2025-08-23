import Header from '../components/Header';
import UploadModal from '../components/UploadModal';
import RestrictModal from '../components/RestrictModal';
import AuthModal from '../components/AuthModal';
import Footer from '../components/Footer';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function PrivacyPolicy() {
  const [content, setContent] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Check if user is logged in (JWT in localStorage)
  const isLoggedIn = !!localStorage.getItem('certalert_jwt');

  useEffect(() => {
    fetch('/privacy_policy.txt')
      .then(res => res.ok ? res.text() : Promise.reject('Failed to load Privacy Policy.'))
      .then(setContent)
      .catch(() => setError('Could not load Privacy Policy. Please try again later.'));
  }, []);

  const [showUpload, setShowUpload] = useState(false);
  const [showRestrictModal, setShowRestrictModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  return (
    <div className="start-page">
      <Header
        showButtons={true}
        onUpload={() => {
          if (!isLoggedIn) setShowAuthModal(true);
          else if (window.localStorage.getItem('certalert_jwt')) {
            fetch('/auth/user', {
              headers: { 'Authorization': `Bearer ${window.localStorage.getItem('certalert_jwt')}` }
            })
              .then(res => res.ok ? res.json() : null)
              .then(data => {
                if (data && data.level === 'free_user') setShowRestrictModal(true);
                else setShowUpload(true);
              });
          } else setShowUpload(true);
        }}
        onLogin={!isLoggedIn ? () => setShowAuthModal(true) : undefined}
        profileButton={isLoggedIn}
        onProfile={isLoggedIn ? () => navigate('/profile') : undefined}
      />
      <RestrictModal
        open={showRestrictModal}
        onClose={() => setShowRestrictModal(false)}
        onSubscribe={() => {
          // Add subscribe logic here later
          setShowRestrictModal(false);
        }}
      />
      {showUpload && <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />}
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', paddingTop: 32, paddingBottom: 32 }}>
        <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 40, minWidth: 500, maxWidth: 1100, width: '90%', display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '60vh' }}>
          <h2 style={{ marginBottom: 24 }}>Privacy Policy</h2>
          {error ? (
            <div style={{ color: '#dc3545', marginBottom: 12 }}>{error}</div>
          ) : (
            <pre style={{ whiteSpace: 'pre-wrap', textAlign: 'left', maxHeight: '50vh', minHeight: '40vh', overflowY: 'auto', width: '100%', fontSize: 17, background: 'none', border: 'none', margin: 0 }}>{content}</pre>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
}
