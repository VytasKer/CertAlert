import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function AuthModal({ onClose }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForgot, setShowForgot] = useState(false)
  const [forgotEmail, setForgotEmail] = useState('')
  const [forgotMsg, setForgotMsg] = useState('')
  const [forgotLoading, setForgotLoading] = useState(false)
  const [agreed, setAgreed] = useState(false)
  const navigate = useNavigate()

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleLogin = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email, password: form.password })
      })
      console.log('Login response:', res);
      if (!res.ok) {
        let msg = 'Login failed. Check your credentials.';
        try {
          const data = await res.json();
          console.log('Login error data:', data);
          if (data && data.detail === 'Account is deactivated. Please contact support.') {
            msg = 'Account is deactivated. Please contact support.';
          }
        } catch (e) { console.log('Login error parsing:', e); }
        throw new Error(msg);
      }
      const data = await res.json()
      console.log('Login success data:', data);
      localStorage.setItem('certalert_jwt', data.access_token)
      setLoading(false)
      onClose()
      navigate('/dashboard')
    } catch (err) {
      console.log('Login catch error:', err);
      setError(err.message || 'Login failed. Check your credentials.')
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    setLoading(true)
    setError('')
    if (form.password !== form.password2) {
      setError('Passwords do not match. Please enter the same password twice.')
      setLoading(false)
      return
    }
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: form.username, email: form.email, password: form.password })
      })
      if (!res.ok) throw new Error('Registration failed')
      const data = await res.json();
      if (data && data.access_token) {
        localStorage.setItem('certalert_jwt', data.access_token);
      }
      setLoading(false)
      onClose()
      navigate('/dashboard')
    } catch (err) {
      setError('Registration failed. Try again.')
      setLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    setForgotLoading(true)
    setForgotMsg('')
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/request-password-reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail })
      })
      setForgotLoading(false)
      setForgotMsg('If your email is registered, a password reset link has been sent.')
    } catch {
      setForgotLoading(false)
      setForgotMsg('Something went wrong. Please try again.')
    }
  }

  const handleKeyDown = e => {
    if (e.key === 'Enter') {
      if (mode === 'login') handleLogin()
      if (mode === 'register') handleRegister()
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <button className="close-btn" onClick={onClose}>×</button>
        {mode === 'login' ? (
          <>
            <h2>Login</h2>
            {!showForgot ? (
              <>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginBottom: 10 }}>
                  <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={form.email}
                    onChange={handleChange}
                    autoFocus
                    onKeyDown={handleKeyDown}
                    style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
                  />
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={form.password}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
                  />
                </div>
                {error && <div className="error">{error}</div>}
                <button
                  onClick={handleLogin}
                  disabled={loading}
                  style={{ background: '#380aab', color: '#fff', border: 'none', borderRadius: 12, padding: '12px 0', width: '100%', fontWeight: 600, fontSize: 17, marginBottom: 10, cursor: loading ? 'not-allowed' : 'pointer' }}
                >
                  {loading ? 'Logging in...' : 'Login'}
                </button>
                <button
                  onClick={() => setMode('register')}
                  disabled={loading}
                  style={{ background: '#380aab', color: '#fff', border: 'none', borderRadius: 12, padding: '12px 0', width: '100%', fontWeight: 600, fontSize: 17, marginBottom: 10, cursor: loading ? 'not-allowed' : 'pointer' }}
                >Register</button>
              </>
            ) : (
              <div style={{ marginTop: 10 }}>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={forgotEmail}
                  onChange={e => setForgotEmail(e.target.value)}
                  style={{ width: '100%', marginBottom: 8 }}
                />
                <button onClick={handleForgotPassword} disabled={forgotLoading || !forgotEmail} style={{ width: '100%' }}>Send reset link</button>
                {forgotMsg && <div style={{ color: '#2563eb', marginTop: 6 }}>{forgotMsg}</div>}
                <div style={{ marginTop: 6 }}>
                  <span style={{ color: '#888', cursor: 'pointer', fontSize: 14 }} onClick={() => setShowForgot(false)}>Back to login</span>
                </div>
              </div>
            )}
            <div style={{ marginTop: 12 }}>
              {!showForgot && (
                <span style={{ color: '#2563eb', cursor: 'pointer', textDecoration: 'underline', fontSize: 15 }} onClick={() => { setShowForgot(true); setForgotMsg(''); }}>Forgot password?</span>
              )}
            </div>
          </>
        ) : (
          <>
            <h2>Register</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginBottom: 10 }}>
              <input
                type="text"
                name="username"
                placeholder="Username"
                value={form.username}
                onChange={handleChange}
                autoFocus
                onKeyDown={handleKeyDown}
                style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
              />
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
              />
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
              />
              <input
                type="password"
                name="password2"
                placeholder="Repeat Password"
                value={form.password2}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                style={{ padding: '14px 16px', fontSize: 18, borderRadius: 16, border: '1.5px solid #ccc', width: '100%' }}
              />
            </div>
            <div style={{ margin: '16px 0 8px 0', display: 'flex', alignItems: 'flex-start', fontSize: 15 }}>
              <input
                type="checkbox"
                id="agree"
                checked={agreed}
                onChange={e => setAgreed(e.target.checked)}
                style={{ marginRight: 8, marginTop: 3 }}
              />
              <label htmlFor="agree" style={{ lineHeight: 1.4 }}>
                I agree to the
                {' '}<Link to="/terms-of-service" target="_blank" style={{ color: '#2563eb', textDecoration: 'underline' }}>Terms of Service</Link>
                {' '}and
                {' '}<Link to="/privacy-policy" target="_blank" style={{ color: '#2563eb', textDecoration: 'underline' }}>Privacy Policy</Link>.
              </label>
            </div>
            {error && <div className="error">{error}</div>}
            <button
              onClick={handleRegister}
              disabled={loading || !agreed || !form.username || !form.email || !form.password || !form.password2}
              style={{
                background: (loading || !agreed || !form.username || !form.email || !form.password || !form.password2) ? '#ccc' : '#380aab',
                color: '#fff',
                border: 'none',
                borderRadius: 12,
                padding: '12px 0',
                width: '100%',
                fontWeight: 600,
                fontSize: 17,
                marginBottom: 10,
                cursor: (loading || !agreed || !form.username || !form.email || !form.password || !form.password2) ? 'not-allowed' : 'pointer'
              }}
            >Register</button>
            <button
              onClick={() => setMode('login')}
              disabled={loading}
              style={{ background: '#380aab', color: '#fff', border: 'none', borderRadius: 12, padding: '12px 0', width: '100%', fontWeight: 600, fontSize: 17, marginBottom: 10, cursor: loading ? 'not-allowed' : 'pointer' }}
            >Back</button>
          </>
        )}
      </div>
    </div>
  )
}
