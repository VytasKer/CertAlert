import { useState } from 'react';
import { usePageTitle } from '../hooks/usePageTitle';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function AdminLogin() {
  usePageTitle('CertAlert - Admin Login');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        setError('Invalid credentials');
        setLoading(false);
        return;
      }
      const data = await res.json();
      localStorage.setItem('certalert_jwt', data.access_token);
      // Fetch user info to check admin status
      const userRes = await fetch(`${BACKEND_BASE_URL}/auth/user`, {
        headers: { 'Authorization': `Bearer ${data.access_token}` }
      });
      if (!userRes.ok) {
        setError('Failed to fetch user info');
        setLoading(false);
        return;
      }
      const user = await userRes.json();
      if (user.level !== 'admin_user') {
        setError('You are not an admin user');
        setLoading(false);
        return;
      }
      window.location.href = '/admin/dashboard';
    } catch {
      setError('Login failed');
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '60px auto', padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
      <h2 style={{ marginBottom: 24 }}>Admin Login</h2>
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: 16 }}>
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        {error && <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>}
        {loading && (
          <div style={{ color: '#2563eb', marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ 
              width: 16, 
              height: 16, 
              border: '2px solid #e5e7eb',
              borderTopColor: '#2563eb',
              borderRadius: '50%',
              marginRight: 8,
              animation: 'spin 1s linear infinite'
            }}></div>
            Connecting to server, please wait...
          </div>
        )}
        <button 
          type="submit" 
          disabled={loading}
          style={{ 
            width: '100%', 
            padding: '10px 0', 
            background: loading ? '#9ca3af' : '#2563eb', 
            color: '#fff', 
            border: 'none', 
            borderRadius: 4, 
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
