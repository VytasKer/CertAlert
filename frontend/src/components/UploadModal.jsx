import { useRef, useState } from 'react'
import './UploadModal.css'

// Get backend base URL from environment
const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || '';

export default function UploadModal({ open, onClose, onUploaded }) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef()
  const [uploading, setUploading] = useState(false)
  const [certName, setCertName] = useState("")

  if (!open) return null

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = async (file) => {
    setError(null)
    setUploading(true)
    try {
      const token = localStorage.getItem('certalert_jwt')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', certName)
      const res = await fetch(`${BACKEND_BASE_URL}/certificates/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })
      if (!res.ok) throw new Error('Upload failed')
      onUploaded && onUploaded()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal upload-modal" onClick={e => e.stopPropagation()}>
        <h2>Upload Certificate</h2>
        <p>Supported formats: PEM (.pem, .crt), DER (.der, .cer)</p>
        <div style={{
          background: '#fff3cd',
          color: '#856404',
          border: '1px solid #ffeeba',
          borderRadius: 6,
          padding: '10px 14px',
          marginBottom: 12,
          fontWeight: 500,
          fontSize: 14
        }}>
          <b>Warning:</b> Do not upload certificates containing private keys. Only upload public certificate files.
        </div>
        <label style={{ display: 'block', marginBottom: 8 }}>
          Certificate Name:
          <input
            type="text"
            value={certName}
            onChange={e => setCertName(e.target.value)}
            placeholder="Enter certificate name"
            style={{ width: '100%', marginTop: 4, marginBottom: 8 }}
            disabled={uploading}
          />
        </label>
        <div
          className={`drop-area${dragActive ? ' active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pem,.crt,.der,.cer"
            ref={inputRef}
            style={{ display: 'none' }}
            onChange={handleChange}
          />
          <div>
            Drag & drop certificate here<br />
            or
            <button
              type="button"
              onClick={() => inputRef.current && inputRef.current.click()}
              disabled={uploading}
              style={{ marginLeft: 8 }}
            >
              Browse
            </button>
          </div>
        </div>
        {uploading && <div>Uploading...</div>}
        {error && <div style={{ color: 'red' }}>{error}</div>}
        <button onClick={onClose} disabled={uploading} style={{ marginTop: 16 }}>Close</button>
      </div>
    </div>
  )
}