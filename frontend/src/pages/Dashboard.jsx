import Header from '../components/Header'
import CertTable from '../components/CertTable'
import Footer from '../components/Footer'
// import FloatingInfoBadge from '../components/FloatingInfoBadge'
import UploadModal from '../components/UploadModal'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Start.css' // Reuse the same styles for consistency
import RestrictModal from '../components/RestrictModal'
import { usePageTitle } from '../hooks/usePageTitle'

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

function Dashboard() {
  usePageTitle('CertAlert - Dashboard');
  
  const navigate = useNavigate()
  const [showUpload, setShowUpload] = useState(false)
  const [showRestrictModal, setShowRestrictModal] = useState(false)
  const [certs, setCerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [user, setUser] = useState(null)
  // Remove uploadError, use modal instead

  const fetchCerts = async () => {
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem('certalert_jwt');
      const resCerts = await fetch(`${BACKEND_BASE_URL}/certificates/user`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!resCerts.ok) throw new Error('Failed to fetch certificates');
      const certData = await resCerts.json();
      setCerts(certData);
      // Fetch user info
      const resUser = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (resUser.ok) setUser(await resUser.json());
      else setUser(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchCerts()
    // eslint-disable-next-line
  }, [])


  const isLoggedIn = !!localStorage.getItem('certalert_jwt');
  const [showAuthModal, setShowAuthModal] = useState(false);
  return (
    <div className="start-page">
      <Header
        onUpload={() => {
          if (!isLoggedIn) setShowAuthModal(true);
          else if (user && user.level === "free_user" && certs.length >= 1) {
            setShowRestrictModal(true);
          } else {
            setShowUpload(true);
          }
        }}
        profileButton={isLoggedIn}
        onProfile={isLoggedIn ? () => navigate('/profile') : undefined}
        onLogin={!isLoggedIn ? () => setShowAuthModal(true) : undefined}
      />
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      <div style={{ marginTop: '2rem' }}>
        {/* RestrictModal for free_user upload limit */}
        <RestrictModal
          open={showRestrictModal}
          onClose={() => setShowRestrictModal(false)}
          onSubscribe={() => {
            // Add subscribe logic here later
            setShowRestrictModal(false);
          }}
        />
        {loading ? (
          <div>Loading certificates...</div>
        ) : error ? (
          <div style={{ color: 'red' }}>{error}</div>
        ) : certs.length === 0 ? (
          <div style={{ color: '#888', fontSize: 20, textAlign: 'center', margin: '3rem 0' }}>
            You have not uploaded any certificates yet.<br />
            Click <b>Upload</b> to add your first certificate!
          </div>
        ) : (
          <>
          {certs.length > 0 && (
            <div style={{
              margin: '0 0 1rem',
              background: '#f0fdf4',
              border: '1px solid #86efac',
              color: '#166534',
              padding: '12px 16px',
              borderRadius: 8,
              fontWeight: 600,
              fontSize: 14,
              boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
            }}>
              You are all set! We will inform you when certificate is soon to expire.
            </div>
          )}
            <CertTable certs={certs} blurred={false} onAction={(cert, action) => {
              if (action === 'rename') fetchCerts()
            }} />
            {user && user.level === 'free_user' && (
              <div style={{ marginTop: 32, textAlign: 'center' }}>
                <div style={{ fontSize: 20, marginBottom: 16, color: '#380aab', fontWeight: 600 }}>
                  Unlock more features and certificate slots by subscribing!
                </div>
                <button
                  style={{ background: '#380aab', color: '#fff', border: 'none', borderRadius: 8, padding: '14px 38px', fontWeight: 600, fontSize: 18, cursor: 'pointer', boxShadow: '0 2px 8px rgba(56,10,171,0.08)' }}
                  onClick={() => navigate('/subscribe')}
                >Subscribe</button>
              </div>
            )}
          </>
        )}
      </div>
      <UploadModal open={showUpload} onClose={() => setShowUpload(false)} onUploaded={fetchCerts} />
      {/* No Welcome message in Dashboard */}
      <Footer />
      {/* <FloatingInfoBadge /> */}
    </div>
  )
}

export default Dashboard