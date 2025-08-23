import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function SubscribeSuccess() {
  const navigate = useNavigate();
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header showButtons={true} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 32 }}>
        <h2 style={{ color: '#2563eb', marginBottom: 24 }}>Thank you for your purchase!</h2>
        <p style={{ fontSize: 18, marginBottom: 32 }}>Your subscription is now active. You can manage your certificates and account in your dashboard.</p>
        <button
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 32px', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
          onClick={() => navigate('/dashboard')}
        >
          Go to Dashboard
        </button>
      </div>
      <Footer />
    </div>
  );
}
