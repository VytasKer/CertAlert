import React, { useState } from 'react'

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function CertTable({ certs = [], blurred, onAction }) {
  const [editId, setEditId] = useState(null)
  const [editValue, setEditValue] = useState("")
  const [saving, setSaving] = useState(false)
  const [infoPopup, setInfoPopup] = useState({ open: false, cert: null, loading: false, error: null })
  const [deletePopup, setDeletePopup] = useState({ open: false, cert: null, loading: false, error: null })

  const handleNameClick = (cert) => {
    setEditId(cert.id)
    setEditValue(cert.name || "")
  }

  const handleSave = async (cert) => {
    setSaving(true)
    try {
      const token = localStorage.getItem('certalert_jwt')
      const res = await fetch(`${BACKEND_BASE_URL}/certificates/${cert.id}/name`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: editValue })
      })
      if (!res.ok) throw new Error('Failed to update name')
      setEditId(null)
      setEditValue("")
      if (onAction) onAction(cert, 'rename')
    } catch (err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleInfo = async (cert) => {
    setInfoPopup({ open: true, cert: null, loading: true, error: null })
    try {
      const token = localStorage.getItem('certalert_jwt')
      const res = await fetch(`${BACKEND_BASE_URL}/certificates/${cert.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to fetch certificate info')
      const data = await res.json()
      setInfoPopup({ open: true, cert: data, loading: false, error: null })
    } catch (err) {
      setInfoPopup({ open: true, cert: null, loading: false, error: err.message })
    }
  }

  const handleDelete = (cert) => {
    setDeletePopup({ open: true, cert, loading: false, error: null })
  }

  const [localCerts, setLocalCerts] = useState(certs)

  // Keep localCerts in sync with certs prop, but only update if array reference or length changes
  React.useEffect(() => {
    if (certs.length !== localCerts.length || !certs.every((c, i) => c.id === localCerts[i]?.id)) {
      setLocalCerts(certs)
    }
  }, [certs])

  const confirmDelete = async () => {
    setDeletePopup(p => ({ ...p, loading: true }))
    try {
      const token = localStorage.getItem('certalert_jwt')
      const res = await fetch(`${BACKEND_BASE_URL}/certificates/${deletePopup.cert.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to delete certificate')
      setDeletePopup({ open: false, cert: null, loading: false, error: null })
      setLocalCerts(prev => prev.filter(c => c.id !== deletePopup.cert.id))
      if (onAction) onAction(deletePopup.cert, 'delete')
    } catch (err) {
      setDeletePopup(p => ({ ...p, loading: false, error: err.message }))
    }
  }

  const [fingerprintPopup, setFingerprintPopup] = useState({ open: false, value: '' })

  const handleFingerprintClick = (fp) => {
    setFingerprintPopup({ open: true, value: fp })
  }

  const closePopup = () => setFingerprintPopup({ open: false, value: '' })

  return (
    <>
    <div className="cert-table">
      <div className="cert-table-header">
        <span>#ID</span>
        <span>Cert Name</span>
        <span>Valid From</span>
        <span>Valid To</span>
        <span>Fingerprint</span>
        <span>Expires In Days</span>
        <span>Action</span>
      </div>
      {localCerts.length === 0 ? (
        <div className="cert-table-row">
          <span colSpan={7} style={{ textAlign: 'center', width: '2600%' }}>
            No certificates found.
          </span>
        </div>
      ) : localCerts.map(cert => (
        <div className={`cert-table-row${blurred ? ' blurred' : ''}`} key={cert.id}>
          <span>{cert.id}</span>
          <span>
            {editId === cert.id ? (
              <>
                <input
                  value={editValue}
                  onChange={e => setEditValue(e.target.value)}
                  disabled={saving}
                  style={{ width: 120 }}
                  autoFocus
                />
                <button onClick={() => handleSave(cert)} disabled={saving || !editValue.trim()} style={{ marginLeft: 4 }}>Save</button>
                <button onClick={() => setEditId(null)} disabled={saving} style={{ marginLeft: 2 }}>Cancel</button>
              </>
            ) : (
              <span
                style={{ cursor: 'pointer', color: '#2563eb', textDecoration: 'underline' }}
                title="Click to edit name"
                onClick={() => handleNameClick(cert)}
              >
                {cert.name || <span style={{ color: '#aaa' }}>[No Name]</span>}
              </span>
            )}
          </span>
          <span>{(cert.valid_from || cert.validFrom || '').slice(0, 10)}</span>
          <span>{(cert.valid_to || cert.validTo || '').slice(0, 10)}</span>
          <span style={{ cursor: 'pointer', color: '#2563eb', textDecoration: 'underline' }}
            title="Click to view full fingerprint"
            onClick={() => handleFingerprintClick(cert.fingerprint)}
          >
            ...{cert.fingerprint?.slice(-10) || ''}
          </span>
          <span style={{ fontWeight: 600 }}>
            {(cert.days_left ?? cert.expiresIn) < 0 ? (
              <span style={{ color: '#dc3545', fontWeight: 700 }}>Expired</span>
            ) : (
              (() => {
                const days = cert.days_left ?? cert.expiresIn;
                const color = days < 30 ? '#ff6a00' : '#000';
                return <span style={{ color, fontWeight: 700 }}>{days}</span>;
              })()
            )}
          </span>
          <span>
            <button onClick={() => handleInfo(cert)}>GET INFO</button>
            {((cert.days_left ?? cert.expiresIn) < 0) ? null : (
              <button onClick={() => handleDelete(cert)}>DELETE</button>
            )}
          </span>
        </div>
      ))}
    </div>
    {fingerprintPopup.open && (
      <div className="modal-overlay" style={{ zIndex: 2000 }} onClick={closePopup}>
        <div className="modal" style={{ minWidth: 340, maxWidth: 600, margin: 'auto', padding: 24 }} onClick={e => e.stopPropagation()}>
          <h3>Certificate Fingerprint</h3>
          <div style={{ wordBreak: 'break-all', fontFamily: 'monospace', fontSize: 16, margin: '1rem 0' }}>{fingerprintPopup.value}</div>
          <button onClick={() => {navigator.clipboard.writeText(fingerprintPopup.value); closePopup();}} style={{ marginRight: 8 }}>Copy</button>
          <button onClick={closePopup}>Close</button>
        </div>
      </div>
    )}
    {infoPopup.open && (
      <div className="modal-overlay" style={{ zIndex: 2100 }} onClick={() => setInfoPopup({ open: false, cert: null, loading: false, error: null })}>
        <div className="modal" style={{ minWidth: 340, maxWidth: 600, margin: 'auto', padding: 24 }} onClick={e => e.stopPropagation()}>
          <h3>Certificate Info</h3>
          {infoPopup.loading ? <div>Loading...</div> : infoPopup.error ? <div style={{ color: 'red' }}>{infoPopup.error}</div> : (
            <div style={{ wordBreak: 'break-all', fontFamily: 'monospace', fontSize: 15, textAlign: 'left' }}>
              <div style={{ marginBottom: 4 }}><b>ID:</b> {infoPopup.cert?.id}</div>
              <div style={{ marginBottom: 4 }}><b>Name:</b> {infoPopup.cert?.name}</div>
              <div style={{ marginBottom: 4 }}><b>File Name:</b> {infoPopup.cert?.file_name}</div>
              <div style={{ marginBottom: 4 }}><b>Issuer:</b> {infoPopup.cert?.issuer}</div>
              <div style={{ marginBottom: 4 }}><b>Subject:</b> {infoPopup.cert?.subject}</div>
              <div style={{ marginBottom: 4 }}><b>Valid From:</b> {(infoPopup.cert?.valid_from || '').slice(0, 10)}</div>
              <div style={{ marginBottom: 4 }}><b>Valid To:</b> {(infoPopup.cert?.valid_to || '').slice(0, 10)}</div>
              <div style={{ marginBottom: 4 }}><b>Serial Number:</b> {infoPopup.cert?.serial_number}</div>
              <div style={{ marginBottom: 4 }}><b>Fingerprint:</b> {infoPopup.cert?.fingerprint}</div>
              <div style={{ marginBottom: 4 }}><b>Days Left:</b> {infoPopup.cert?.days_left}</div>
            </div>
          )}
          <button onClick={() => setInfoPopup({ open: false, cert: null, loading: false, error: null })} style={{ marginTop: 16 }}>Close</button>
        </div>
      </div>
    )}
    {deletePopup.open && (
      <div className="modal-overlay" style={{ zIndex: 2200 }} onClick={() => setDeletePopup({ open: false, cert: null, loading: false, error: null })}>
        <div className="modal" style={{ minWidth: 340, maxWidth: 500, margin: 'auto', padding: 24 }} onClick={e => e.stopPropagation()}>
          <h3>Delete Certificate</h3>
          <div style={{ margin: '1rem 0' }}>Are you sure you want to delete this certificate?</div>
          {deletePopup.error && <div style={{ color: 'red' }}>{deletePopup.error}</div>}
          <button onClick={confirmDelete} disabled={deletePopup.loading} style={{ marginRight: 8, background: '#dc3545' }}>Yes, Delete</button>
          <button onClick={() => setDeletePopup({ open: false, cert: null, loading: false, error: null })} disabled={deletePopup.loading}>No</button>
        </div>
      </div>
    )}
    </>
  )
}