import React from 'react';
import { useNavigate } from 'react-router-dom';

const RestrictModal = ({ open, onClose, onSubscribe }) => {
  const navigate = useNavigate();
  if (!open) return null;
  const handleSubscribe = () => {
    if (onSubscribe) onSubscribe();
    navigate('/subscribe');
  };
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.3)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '1rem',
        boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
        minWidth: 320,
        textAlign: 'center'
      }}>
        <h2 style={{ color: '#d97706', marginBottom: '1rem' }}>Upgrade Required</h2>
        <p style={{ marginBottom: '2rem', fontWeight: 500 }}>
          You have to be subscribed to upload more than 1 certificate.
        </p>
        <button
          style={{
            backgroundColor: '#380aab',
            color: 'white',
            padding: '0.75rem 2rem',
            border: 'none',
            borderRadius: '1rem',
            fontSize: '1rem',
            cursor: 'pointer',
            marginRight: '1rem',
            boxShadow: '0 2px 8px rgba(56,10,171,0.08)'
          }}
          onClick={handleSubscribe}
        >
          Subscribe
        </button>
        <button
          style={{
            backgroundColor: '#e5e7eb',
            color: '#111827',
            padding: '0.75rem 2rem',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '1rem',
            cursor: 'pointer',
            marginLeft: '1rem'
          }}
          onClick={onClose}
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default RestrictModal;
