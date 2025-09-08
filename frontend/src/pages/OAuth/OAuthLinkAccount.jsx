// frontend/src/pages/OAuth/OAuthLinkAccount.jsx

import React from 'react';
import AccountLinkingForm from '../../components/OAuth/AccountLinkingForm';

const OAuthLinkAccount = () => {
  const handleLinkSuccess = (data) => {
    console.log('Account linking successful:', data);
    // Additional success handling can be added here
  };

  const handleLinkError = (error) => {
    console.error('Account linking error:', error);
    // Additional error handling can be added here
  };

  return (
    <AccountLinkingForm 
      onLinkSuccess={handleLinkSuccess}
      onLinkError={handleLinkError}
    />
  );
};

export default OAuthLinkAccount;
