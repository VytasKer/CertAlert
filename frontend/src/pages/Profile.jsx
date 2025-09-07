import Header from '../components/Header'
import Footer from '../components/Footer'
import UploadModal from '../components/UploadModal'
import RestrictModal from '../components/RestrictModal'
import { useState, useEffect } from 'react'
import ConfirmModal from '../components/ConfirmModal'
import { useNavigate } from 'react-router-dom'
import './Start.css'
import ChangePasswordModal from '../components/ChangePasswordModal'
import AuthModal from '../components/AuthModal'
import { usePageTitle } from '../hooks/usePageTitle'

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

function Spinner() {
  return <span style={{ marginLeft: 8 }}>⏳</span>;
}

export default function Profile() {
  usePageTitle('CertAlert - Profile');
  
  const [showUpload, setShowUpload] = useState(false)
  const [showRestrictModal, setShowRestrictModal] = useState(false)
  const [user, setUser] = useState(null)
  const [activeTab, setActiveTab] = useState('user')
  const [subscriptions, setSubscriptions] = useState([])
  const [showDeactivate, setShowDeactivate] = useState(false)
  const [deactivateLoading, setDeactivateLoading] = useState(false)
  const [deactivateError, setDeactivateError] = useState('')
  const [showChangePw, setShowChangePw] = useState(false)
  const [loadingSubId, setLoadingSubId] = useState(null)
  const handleDownloadInvoice = async (subId) => {
    setLoadingSubId(subId);
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/subscriptions/invoice/${subId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Invoice not available');
      const { invoice_pdf_url } = await res.json();
      window.open(invoice_pdf_url, '_blank');
    } catch (err) {
      alert(err.message);
    } finally {
      setLoadingSubId(null);
    }
  };
  const [changePwLoading, setChangePwLoading] = useState(false)
  const [changePwError, setChangePwError] = useState('')
  const [changePwSuccess, setChangePwSuccess] = useState('')
  const [changePwConfirm, setChangePwConfirm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch user info from backend (run once on mount)
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem('certalert_jwt');
        const res = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Failed to fetch user info');
        setUser(await res.json());
      } catch {
        setUser(null);
      }
    };
    fetchUser();
  }, []);

  useEffect(() => {
    // Fetch user subscriptions only when user is loaded
    if (!user || !user.id) return;
    const fetchSubscriptions = async () => {
      try {
        const token = localStorage.getItem('certalert_jwt');
        const res = await fetch(`${BACKEND_BASE_URL}/subscriptions/byuser/${user.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setSubscriptions(await res.json());
        else setSubscriptions([]);
      } catch {
        setSubscriptions([]);
      }
    };
    fetchSubscriptions();
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem('certalert_jwt')
    navigate('/')
  }

  const handleDeactivate = async () => {
    if (!user) return;
    setDeactivateLoading(true);
    setDeactivateError('');
    try {
      const token = localStorage.getItem('certalert_jwt');
      const res = await fetch(`${BACKEND_BASE_URL}/users/deactivate/${user.id}`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to deactivate account');
      }
      setDeactivateLoading(false);
      localStorage.removeItem('certalert_jwt');
      setShowDeactivate(false);
      alert('Your account has been deactivated.');
      navigate('/');
    } catch (err) {
      setDeactivateError(err.message || 'Failed to deactivate account');
      setDeactivateLoading(false);
    }
  };

  const handleChangePw = async () => {
    setChangePwLoading(true)
    setChangePwError('')
    setChangePwSuccess('')
    if (!user) return
    try {
      // For security, trigger backend to send reset email to user email
      const token = localStorage.getItem('certalert_jwt')
      const res = await fetch(`${BACKEND_BASE_URL}/auth/request-password-reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ email: user.email })
      })
      setChangePwLoading(false)
      setChangePwSuccess('A password change link has been sent to your email.')
    } catch {
      setChangePwLoading(false)
      setChangePwError('Failed to send password change email.')
    }
  }

  const isLoggedIn = !!localStorage.getItem('certalert_jwt');
  const [showAuthModal, setShowAuthModal] = useState(false);
  return (
    <div className="start-page">
      <Header
        onUpload={() => {
          if (!isLoggedIn) setShowAuthModal(true);
          else if (user && user.level === "free_user") {
            setShowRestrictModal(true);
          } else {
            setShowUpload(true);
          }
        }}
        dashboardButton={isLoggedIn}
        onDashboard={isLoggedIn ? () => navigate('/dashboard') : undefined}
        onLogin={!isLoggedIn ? () => setShowAuthModal(true) : undefined}
      />
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      <div style={{ marginTop: '2rem', display: 'flex', maxWidth: 1400, minHeight: 500, background: 'transparent', marginLeft: 'auto', marginRight: 'auto', width: '100%' }}>
        {/* Left side: Tabs */}
        <div style={{ width: 260, minWidth: 220, maxWidth: 320, background: '#f7f7fa', borderRadius: 8, padding: '32px 16px', marginRight: 40, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
          <button
            onClick={() => setActiveTab('user')}
            style={{
              background: 'none',
              border: 'none',
              fontWeight: activeTab === 'user' ? 700 : 400,
              fontSize: 18,
              marginBottom: 18,
              color: activeTab === 'user' ? '#2563eb' : '#222',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%'
            }}
          >User Information</button>
          <button
            onClick={() => setActiveTab('subscriptions')}
            style={{
              background: 'none',
              border: 'none',
              fontWeight: activeTab === 'subscriptions' ? 700 : 400,
              fontSize: 18,
              marginBottom: 18,
              color: activeTab === 'subscriptions' ? '#2563eb' : '#222',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%'
            }}
          >My Subscriptions</button>
          <button
            onClick={() => setActiveTab('settings')}
            style={{
              background: 'none',
              border: 'none',
              fontWeight: activeTab === 'settings' ? 700 : 400,
              fontSize: 18,
              marginBottom: 18,
              color: activeTab === 'settings' ? '#2563eb' : '#222',
              cursor: 'pointer',
              textAlign: 'left',
              width: '100%'
            }}
          >Settings</button>
          <div style={{ flex: 1 }} />
          <button
            onClick={handleLogout}
            style={{ background: '#dc3545', color: '#fff', border: 'none', borderRadius: 4, padding: '10px 0', width: '100%', fontWeight: 600, fontSize: 16, marginTop: 24, cursor: 'pointer' }}
          >Logout</button>
        </div>
        {/* Right side: Tab content */}
        <div style={{ flex: '0 1 1000px', width: 1000, minWidth: 600, maxWidth: 1100, background: '#fff', borderRadius: 8, padding: '32px 48px', boxShadow: '0 2px 8px rgba(0,0,0,0.07)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', minHeight: 0, transition: 'width 0.2s', overflow: 'auto' }}>
          {activeTab === 'user' && (
            <>
              <h2 style={{ marginTop: 0, marginBottom: 24 }}>User Information</h2>
              {user ? (
                <div style={{ fontSize: 17, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left', width: '100%' }}>
                  <div style={{ marginBottom: 10 }}><b>User ID:</b> <span style={{ marginLeft: 8 }}>{user.id}</span></div>
                  <div style={{ marginBottom: 10 }}><b>Username:</b> <span style={{ marginLeft: 8 }}>{user.username}</span></div>
                  <div style={{ marginBottom: 10 }}><b>Email:</b> <span style={{ marginLeft: 8 }}>{user.email}</span></div>
                  <div style={{ marginBottom: 10 }}><b>User Level:</b> <span style={{ marginLeft: 8 }}>{user.level}</span></div>
                  <div style={{ marginBottom: 10 }}><b>User registered at:</b> <span style={{ marginLeft: 8 }}>{user.created_at ? new Date(user.created_at).toLocaleString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ''}</span></div>
                </div>
              ) : (
                <div>Loading user info...</div>
              )}
            </>
          )}
          {activeTab === 'subscriptions' && (
            <>
              <h2 style={{ marginTop: 0, marginBottom: 24 }}>My Subscriptions</h2>
              <button
                onClick={() => navigate('/subscribe')}
                disabled={user && user.level === 'subscribed_user'}
                style={{
                  background: user && user.level === 'subscribed_user' ? '#e5e7eb' : '#2563eb',
                  color: user && user.level === 'subscribed_user' ? '#888' : '#fff',
                  border: 'none',
                  borderRadius: 4,
                  padding: '12px 32px',
                  fontWeight: 600,
                  fontSize: 16,
                  marginBottom: 24,
                  cursor: user && user.level === 'subscribed_user' ? 'not-allowed' : 'pointer'
                }}
              >Select a Plan</button>
              <div style={{ width: '100%', overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 8 }}>
                  <thead>
                    <tr style={{ background: '#f7f7fa' }}>
                      <th style={{ padding: '10px 8px', borderBottom: '1px solid #eee' }}>Subscription ID</th>
                      <th style={{ padding: '10px 8px', borderBottom: '1px solid #eee' }}>Status</th>
                      <th style={{ padding: '10px 8px', borderBottom: '1px solid #eee' }}>Start Date</th>
                      <th style={{ padding: '10px 8px', borderBottom: '1px solid #eee' }}>End Date</th>
                      <th style={{ padding: '10px 8px', borderBottom: '1px solid #eee' }}>Invoice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {subscriptions.length === 0 ? (
                      <tr><td colSpan={5} style={{ textAlign: 'center', padding: 16, color: '#888' }}>No subscriptions found.</td></tr>
                    ) : (
                      subscriptions.map(sub => (
                        <tr key={sub.sub_id}>
                          <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>{sub.sub_id}</td>
                          <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>{sub.sub_status}</td>
                          <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>{sub.sub_start_date ? new Date(sub.sub_start_date).toLocaleDateString() : ''}</td>
                          <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>{sub.sub_end_date ? new Date(sub.sub_end_date).toLocaleDateString() : ''}</td>
                          <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                            {(sub.sub_status === "ACTIVATED" || sub.sub_status === "DEACTIVATED") && (
                              <button onClick={() => handleDownloadInvoice(sub.sub_id)} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '6px 16px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>
                                {loadingSubId === sub.sub_id ? <Spinner /> : "Invoice"}
                              </button>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
          {activeTab === 'settings' && (
            <>
              <h2 style={{ marginTop: 0, marginBottom: 24 }}>Settings</h2>
              <button
                onClick={() => { setShowChangePw(true); setChangePwConfirm(false); }}
                style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '12px 0', width: 220, fontWeight: 600, fontSize: 16, marginBottom: 16, cursor: 'pointer' }}
              >Change Password</button>
              <ChangePasswordModal
                open={showChangePw}
                onClose={() => { setShowChangePw(false); setChangePwError(''); setChangePwSuccess(''); setChangePwConfirm(false); }}
                onConfirm={() => { setChangePwConfirm(true); handleChangePw(); }}
                onSubmit={handleChangePw}
                loading={changePwLoading}
                error={changePwError}
                success={changePwSuccess}
                confirm={!changePwConfirm}
              />
              <button
                onClick={() => setShowDeactivate(true)}
                style={{ background: '#dc3545', color: '#fff', border: 'none', borderRadius: 4, padding: '12px 0', width: 220, fontWeight: 600, fontSize: 16, marginTop: 8, cursor: 'pointer' }}
              >Deactivate Account</button>
              <ConfirmModal
                open={showDeactivate}
                onClose={() => { setShowDeactivate(false); setDeactivateError(''); }}
                onConfirm={handleDeactivate}
                title="Deactivate Account"
                message="Are you sure you want to deactivate your account? This will delete all your certificates and you will not be able to log in until reactivated by an admin. This action cannot be undone."
                confirmText="Deactivate"
                cancelText="Cancel"
                loading={deactivateLoading}
              />
              {deactivateError && <div style={{ color: '#dc3545', marginTop: 12 }}>{deactivateError}</div>}
            </>
          )}
        </div>
      </div>
      <RestrictModal
        open={showRestrictModal}
        onClose={() => setShowRestrictModal(false)}
        onSubscribe={() => {
          // Add subscribe logic here later
          setShowRestrictModal(false);
        }}
      />
      <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />
      <Footer />
    </div>
  )
}
