import React from 'react';

export default function ConfirmModal({ open, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', loading }) {
  if (!open) return null;
  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: '#fff', borderRadius: 8, padding: 32, minWidth: 320, boxShadow: '0 2px 16px rgba(0,0,0,0.12)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h3 style={{ margin: 0, marginBottom: 16 }}>{title}</h3>
        <div style={{ marginBottom: 24, color: '#444', textAlign: 'center' }}>{message}</div>
        <div style={{ display: 'flex', gap: 16 }}>
          <button onClick={onClose} disabled={loading} style={{ padding: '8px 20px', borderRadius: 4, border: '1px solid #bbb', background: '#f7f7fa', color: '#333', fontWeight: 500, cursor: 'pointer' }}>{cancelText}</button>
          <button onClick={onConfirm} disabled={loading} style={{ padding: '8px 20px', borderRadius: 4, border: 'none', background: '#dc3545', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>{loading ? 'Processing...' : confirmText}</button>
        </div>
      </div>
    </div>
  );
}