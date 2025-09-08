// frontend/src/pages/OAuth/OAuthSuccess.jsx

import React from 'react';
import OAuthCallback from '../../components/OAuth/OAuthCallback';

const OAuthSuccess = () => {
  const handleAuthSuccess = (data) => {
    console.log('OAuth authentication successful:', data);
    // Additional success handling can be added here
  };

  const handleAuthError = (error) => {
    console.error('OAuth authentication error:', error);
    // Additional error handling can be added here
  };

  const handleAccountLinkingRequired = (linkingData) => {
    console.log('Account linking required:', linkingData);
    // Additional account linking handling can be added here
  };

  return (
    <OAuthCallback 
      onAuthSuccess={handleAuthSuccess}
      onAuthError={handleAuthError}
      onAccountLinkingRequired={handleAccountLinkingRequired}
    />
  );
};

export default OAuthSuccess;
