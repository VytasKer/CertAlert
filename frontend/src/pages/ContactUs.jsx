import Header from '../components/Header';
import UploadModal from '../components/UploadModal';
import RestrictModal from '../components/RestrictModal';
import AuthModal from '../components/AuthModal';
import Footer from '../components/Footer';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ContactUs() {
  const [email, setEmail] = useState('');
  const [topic, setTopic] = useState('');
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const isLoggedIn = !!localStorage.getItem('certalert_jwt');

  useEffect(() => {
    if (isLoggedIn) {
      const token = localStorage.getItem('certalert_jwt');
      fetch('/auth/user', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data && data.email) setEmail(data.email);
        });
    }
  }, [isLoggedIn]);

  // Simple email validation
  const isValidEmail = email => /.+@.+\..+/.test(email);

  const handleFileChange = e => {
    const f = e.target.files[0];
    if (f && f.size > 2 * 1024 * 1024) {
      setError('File size must be less than 2MB.');
      setFile(null);
    } else {
      setError('');
      setFile(f);
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!email || !topic || !message) {
      setError('Please fill in all required fields.');
      return;
    }
    if (!isValidEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }
    if (topic.length > 100 || email.length > 100 || message.length > 1000) {
      setError('One or more fields exceed the allowed length.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('topic', topic);
      formData.append('message', message);
      if (file) {
        formData.append('file', file);
      }
      const res = await fetch('/auth/contact-query', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to send query.');
      }
      setSuccess('Your query has been sent successfully!');
    } catch (err) {
      setError(err.message || 'Failed to send query.');
    }
  };

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
            // Fetch user info for level
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
        <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', padding: 40, minWidth: 500, maxWidth: 700, width: '90%', display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '60vh' }}>
          <h2 style={{ marginBottom: 24 }}>Contact Us</h2>
          <div style={{ width: '100%', marginBottom: 18 }}>
            <label htmlFor="email" style={{ fontWeight: 500 }}>
              Your Email <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              maxLength={100}
              style={{ width: '100%', padding: 10, fontSize: 16, borderRadius: 4, border: '1px solid #ccc', marginTop: 6 }}
              required
            />
          </div>
          <div style={{ width: '100%', marginBottom: 18 }}>
            <label htmlFor="topic" style={{ fontWeight: 500 }}>
              Topic <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              maxLength={100}
              style={{ width: '100%', padding: 10, fontSize: 16, borderRadius: 4, border: '1px solid #ccc', marginTop: 6 }}
              required
            />
          </div>
          <div style={{ width: '100%', marginBottom: 18 }}>
            <label htmlFor="message" style={{ fontWeight: 500 }}>
              Your Concern <span style={{ color: 'red' }}>*</span>
            </label>
            <textarea
              id="message"
              value={message}
              onChange={e => setMessage(e.target.value)}
              maxLength={1000}
              style={{ width: '100%', minHeight: 100, padding: 10, fontSize: 16, borderRadius: 4, border: '1px solid #ccc', marginTop: 6, resize: 'vertical' }}
              required
            />
          </div>
          <div style={{ width: '100%', marginBottom: 18 }}>
            <label htmlFor="file" style={{ fontWeight: 500 }}>
              Attach file (optional, max 2MB)
            </label>
            <input
              id="file"
              type="file"
              accept="image/*,.pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              style={{ marginTop: 6 }}
            />
          </div>
          {error && <div style={{ color: '#dc3545', marginBottom: 12 }}>{error}</div>}
          {success && <div style={{ color: '#198754', marginBottom: 12 }}>{success}</div>}
          <button type="submit" style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '12px 0', width: '100%', fontWeight: 600, fontSize: 16 }}>
            Send Query
          </button>
        </form>
      </div>
      <Footer />
    </div>
  );
}