import logoHeader from '../../resources/certalert-logo-header.jpg';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Usage:
// - In Dashboard: pass onUpload (shows upload modal), profileButton=true, onProfile (shows profile modal)
// - In Start: pass onUpload (shows auth modal), onLogin (shows auth modal), profileButton not set
export default function Header({ onUpload, profileButton, onProfile, onLogin, dashboardButton, onDashboard, showButtons = true }) {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  const handleLogoClick = () => {
    if (isLoggedIn) navigate('/dashboard');
    else navigate('/start');
  };
  return (
    <header className="header">
      <div className="logo" style={{ cursor: 'pointer', padding: 0 }} onClick={handleLogoClick}>
        <img src={logoHeader} alt="CertAlert Logo" style={{ height: 40, verticalAlign: 'middle' }} />
      </div>
      {showButtons && (
        <div className="header-actions">
          <button onClick={onUpload}>Upload</button>
          {dashboardButton && <button onClick={onDashboard}>Dashboard</button>}
          {profileButton && <button onClick={onProfile}>Profile</button>}
          {!profileButton && onLogin && <button onClick={onLogin}>Login</button>}
        </div>
      )}
    </header>
  )
}