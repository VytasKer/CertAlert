import Header from '../components/Header';
import Footer from '../components/Footer';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import RestrictModal from '../components/RestrictModal';
import UploadModal from '../components/UploadModal';
import AuthModal from '../components/AuthModal';
import './Start.css';
import { usePageTitle } from '../hooks/usePageTitle';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

// Helper to fetch user info
async function fetchUser(jwt) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
      headers: { 'Authorization': `Bearer ${jwt}` }
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// Helper to fetch certs
async function fetchCerts(jwt) {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/certificates/user`, {
      headers: { 'Authorization': `Bearer ${jwt}` }
    });
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

// Stripe Price IDs (loaded from environment variables)
const YEARLY_PRICE_ID = import.meta.env.VITE_STRIPE_YEARLY_PRICE_ID;
const THREE_YEAR_PRICE_ID = import.meta.env.VITE_STRIPE_THREE_YEAR_PRICE_ID;
const FIVE_YEAR_PRICE_ID = import.meta.env.VITE_STRIPE_FIVE_YEAR_PRICE_ID;

export default function Subscribe() {
  usePageTitle('CertAlert - Subscribe');
  
  const navigate = useNavigate();
  const jwt = localStorage.getItem('certalert_jwt');
  const isLoggedIn = !!jwt;
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showRestrictModal, setShowRestrictModal] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [user, setUser] = useState(null);
  const [certs, setCerts] = useState([]);

  useEffect(() => {
    if (isLoggedIn) {
      fetchUser(jwt).then(setUser);
      fetchCerts(jwt).then(setCerts);
    }
  }, [isLoggedIn, jwt]);

  // Upload button logic
  const handleUpload = async () => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
      return;
    }
    // If user/certs not loaded, fetch them
    let currentUser = user;
    let currentCerts = certs;
    if (!currentUser) currentUser = await fetchUser(jwt);
    if (!currentCerts) currentCerts = await fetchCerts(jwt);
    if (currentUser && currentUser.level === 'free_user' && currentCerts.length >= 1) {
      setShowRestrictModal(true);
    } else {
      setShowUpload(true);
    }
  };

  return (
    <div className="start-page">
      <Header
        showButtons={true}
        onUpload={handleUpload}
        dashboardButton={isLoggedIn}
        onDashboard={isLoggedIn ? () => navigate('/dashboard') : undefined}
        onLogin={!isLoggedIn ? () => setShowAuthModal(true) : undefined}
      />
      {/* Modals */}
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      {showRestrictModal && <RestrictModal open={showRestrictModal} onClose={() => setShowRestrictModal(false)} onSubscribe={() => { setShowRestrictModal(false); navigate('/subscribe'); }} />}
      {showUpload && <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />}
      <div style={{ minHeight: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', paddingTop: 32, paddingBottom: 32 }}>
        <h2 style={{ marginBottom: 32 }}>Choose Your Subscription Plan</h2>
        <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', width: '100%' }}>
          {/* Yearly Plan */}
          <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 32, minWidth: 280, maxWidth: 340, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h3 style={{ marginBottom: 12 }}>Yearly Subscription</h3>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#2563eb', marginBottom: 8 }}>10 EUR</div>
            <div style={{ marginBottom: 18, textAlign: 'center' }}>
              Less than 1 EUR per Month!<br />
              Up to 20 certificate uploads.<br />
              Email alerts before expiry.<br />
              Basic certificate and encryption-related support.
            </div>
            {/* Price ID hidden for security */}
            <button
              style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
              onClick={async () => {
                const jwt = localStorage.getItem('certalert_jwt');
                if (!jwt) {
                  setShowAuthModal(true);
                  return;
                }
                // Get user_id from localStorage or backend (adjust as needed)
                let user_id = localStorage.getItem('certalert_user_id');
                if (!user_id) {
                  // Try to fetch user info from backend as fallback
                  try {
                    const res = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
                      headers: { 'Authorization': `Bearer ${jwt}` }
                    });
                    const user = await res.json();
                    if (user && user.id) {
                      user_id = user.id;
                      localStorage.setItem('certalert_user_id', user_id);
                    }
                  } catch (err) {
                    // ignore
                  }
                }
                if (!user_id) {
                  alert('User ID not found. Please log in again.');
                  setShowAuthModal(true);
                  return;
                }
                // Generate success/cancel URLs
                const success_url = window.location.origin + '/subscribe-processing';
                const cancel_url = window.location.origin + '/subscribe-cancel';
                const res = await fetch(`${BACKEND_BASE_URL}/subscriptions/create-checkout-session`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`,
                  },
                  body: JSON.stringify({
                    price_id: YEARLY_PRICE_ID,
                    user_id,
                    success_url,
                    cancel_url,
                    // sub_id removed; backend will generate
                  }),
                });
                const data = await res.json();
                if (data.checkout_url) {
                  window.location.href = data.checkout_url;
                } else {
                  alert('Failed to create Stripe session.');
                }
              }}
            >
              Select this plan
            </button>
          </div>
          {/* 3 Year Plan */}
          <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 32, minWidth: 280, maxWidth: 340, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h3 style={{ marginBottom: 12 }}>3 Year Subscription</h3>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#2563eb', marginBottom: 8 }}>24 EUR</div>
            <div style={{ marginBottom: 18, textAlign: 'center' }}>
              Up to 20 certificate uploads.<br />
              Email alerts before expiry.<br />
              Basic certificate and encryption-related support.
            </div>
            {/* Price ID hidden for security */}
            <button
              style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
              onClick={async () => {
                const jwt = localStorage.getItem('certalert_jwt');
                if (!jwt) {
                  setShowAuthModal(true);
                  return;
                }
                let user_id = localStorage.getItem('certalert_user_id');
                if (!user_id) {
                  try {
                    const res = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
                      headers: { 'Authorization': `Bearer ${jwt}` }
                    });
                    const user = await res.json();
                    if (user && user.id) {
                      user_id = user.id;
                      localStorage.setItem('certalert_user_id', user_id);
                    }
                  } catch (err) {}
                }
                if (!user_id) {
                  alert('User ID not found. Please log in again.');
                  setShowAuthModal(true);
                  return;
                }
                const success_url = window.location.origin + '/subscribe-processing';
                const cancel_url = window.location.origin + '/subscribe-cancel';
                const res = await fetch(`${BACKEND_BASE_URL}/subscriptions/create-checkout-session`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`,
                  },
                  body: JSON.stringify({
                    price_id: THREE_YEAR_PRICE_ID,
                    user_id,
                    success_url,
                    cancel_url,
                    // sub_id removed; backend will generate
                  }),
                });
                const data = await res.json();
                if (data.checkout_url) {
                  window.location.href = data.checkout_url;
                } else {
                  alert('Failed to create Stripe session.');
                }
              }}
            >
              Select this plan
            </button>
          </div>
          {/* 5 Year Plan */}
          <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 32, minWidth: 280, maxWidth: 340, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h3 style={{ marginBottom: 12 }}>5 Year Subscription</h3>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#2563eb', marginBottom: 8 }}>40 EUR</div>
            <div style={{ marginBottom: 18, textAlign: 'center' }}>
              Up to 20 certificate uploads.<br />
              Email alerts before expiry.<br />
              Basic certificate and encryption-related support.
            </div>
            {/* Price ID hidden for security */}
            <button
              style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
              onClick={async () => {
                const jwt = localStorage.getItem('certalert_jwt');
                if (!jwt) {
                  setShowAuthModal(true);
                  return;
                }
                let user_id = localStorage.getItem('certalert_user_id');
                if (!user_id) {
                  try {
                    const res = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
                      headers: { 'Authorization': `Bearer ${jwt}` }
                    });
                    const user = await res.json();
                    if (user && user.id) {
                      user_id = user.id;
                      localStorage.setItem('certalert_user_id', user_id);
                    }
                  } catch (err) {}
                }
                if (!user_id) {
                  alert('User ID not found. Please log in again.');
                  setShowAuthModal(true);
                  return;
                }
                const success_url = window.location.origin + '/subscribe-processing';
                const cancel_url = window.location.origin + '/subscribe-cancel';
                const res = await fetch(`${BACKEND_BASE_URL}/subscriptions/create-checkout-session`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`,
                  },
                  body: JSON.stringify({
                    price_id: FIVE_YEAR_PRICE_ID,
                    user_id,
                    success_url,
                    cancel_url,
                    // sub_id removed; backend will generate
                  }),
                });
                const data = await res.json();
                if (data.checkout_url) {
                  window.location.href = data.checkout_url;
                } else {
                  alert('Failed to create Stripe session.');
                }
              }}
            >
              Select this plan
            </button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
