import { useState } from 'react';
import { usePageTitle } from '../hooks/usePageTitle';

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function AdminLogin() {
  usePageTitle('CertAlert - Admin Login');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        setError('Invalid credentials');
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
        return;
      }
      const user = await userRes.json();
      if (user.level !== 'admin_user') {
        setError('You are not an admin user');
        return;
      }
      window.location.href = '/admin/dashboard';
    } catch {
      setError('Login failed');
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
        <button type="submit" style={{ width: '100%', padding: '10px 0', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 600 }}>Login</button>
      </form>
    </div>
  );
}
