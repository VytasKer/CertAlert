import Header from '../components/Header';
import Footer from '../components/Footer';
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Extract token from URL
  const params = new URLSearchParams(location.search);
  const token = params.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!password || !confirmPassword) {
      setError('Please fill in both password fields.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password, confirm_password: confirmPassword })
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to reset password.');
      }
      setSuccess('Password changed successfully! Redirecting to start page...');
      setTimeout(() => navigate('/'), 5000);
    } catch (err) {
      setError(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="start-page">
      <Header showButtons={false} />
      <div style={{ minHeight: 400, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 32, minWidth: 340, maxWidth: 400, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h2 style={{ marginBottom: 24 }}>Reset Password</h2>
          <input
            type="password"
            placeholder="New Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{ marginBottom: 16, width: '100%', padding: 10, fontSize: 16, borderRadius: 4, border: '1px solid #ccc' }}
            autoComplete="new-password"
          />
          <input
            type="password"
            placeholder="Confirm New Password"
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            style={{ marginBottom: 16, width: '100%', padding: 10, fontSize: 16, borderRadius: 4, border: '1px solid #ccc' }}
            autoComplete="new-password"
          />
          {error && <div style={{ color: '#dc3545', marginBottom: 12 }}>{error}</div>}
          {success && <div style={{ color: '#198754', marginBottom: 12 }}>{success}</div>}
          <button type="submit" disabled={loading} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '12px 0', width: '100%', fontWeight: 600, fontSize: 16 }}>
            {loading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>
      <Footer />
    </div>
  );
}
