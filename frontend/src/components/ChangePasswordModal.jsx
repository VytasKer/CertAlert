import { useState } from 'react'

export default function ChangePasswordModal({ open, onClose, onSubmit, onConfirm, loading, error, success, confirm }) {
  if (!open) return null
  return (
    <div className="modal-backdrop">
      <div className="modal">
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>Change Password</h2>
        {confirm ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, width: 320 }}>
            <div style={{ marginBottom: 8 }}>Do you really want to change your password?</div>
            <button onClick={onConfirm} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '10px 0', width: '100%', fontWeight: 600, fontSize: 16 }}>
              Yes, send reset link
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, width: 320 }}>
            {loading && <div>Sending reset link...</div>}
            {error && <div style={{ color: '#dc3545' }}>{error}</div>}
            {success && <div style={{ color: '#198754' }}>{success}</div>}
            {(!loading && (success || error)) && (
              <button onClick={onClose} style={{ marginTop: 8, background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, padding: '10px 0', width: '100%', fontWeight: 600, fontSize: 16 }}>Close</button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
