import React from 'react';
import { useAuth } from '../hooks/useAuth';

export default function Welcome() {
  const { isLoggedIn, isLoading } = useAuth();

  // Don't render dynamic content until we've checked login status
  if (isLoading) {
    return (
      <div className="welcome-message">
        <h2>Welcome to CertAlert!</h2>
        <p>The best place to manage, track, and get notified about your certificates.</p>
      </div>
    );
  }
  
  return (
    <div className="welcome-message">
      <h2>Welcome to CertAlert!</h2>
      <p>The best place to manage, track, and get notified about your certificates.</p>
      {isLoggedIn ? (
        <p>Try uploading your first certificate now!</p>
      ) : (
        <p>Login to start managing your certificates and never miss an expiration again!</p>
      )}
    </div>
  )
}