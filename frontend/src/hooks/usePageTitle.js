// src/hooks/usePageTitle.js

import { useEffect } from 'react';

/**
 * Custom hook to dynamically set the browser tab title
 * @param {string} title - The title to set for the current page
 */
export const usePageTitle = (title) => {
  useEffect(() => {
    const originalTitle = document.title;
    
    // Set the new title
    document.title = title;
    
    // Cleanup function to restore original title if needed
    return () => {
      // Only restore if the title hasn't been changed by another component
      if (document.title === title) {
        document.title = originalTitle;
      }
    };
  }, [title]);
};

/**
 * Helper function to generate consistent page titles
 * @param {string} pageName - The specific page name
 * @returns {string} - Formatted title
 */
export const formatPageTitle = (pageName) => {
  if (!pageName || pageName === 'Home') {
    return 'CertAlert';
  }
  return `CertAlert - ${pageName}`;
};
