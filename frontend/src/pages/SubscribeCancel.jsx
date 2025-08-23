import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function SubscribeCancel() {
  const navigate = useNavigate();
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header showButtons={true} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 32 }}>
        <h2 style={{ color: '#e53e3e', marginBottom: 24 }}>Payment Not Completed</h2>
        <p style={{ fontSize: 18, marginBottom: 32 }}>Your payment was not completed. No changes have been made to your account.</p>
        <button
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </button>
      </div>
      <Footer />
    </div>
  );
}
