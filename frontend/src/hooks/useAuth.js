import { useState, useEffect } from 'react';

/**
 * Custom hook to manage authentication state safely
 * Prevents hydration mismatches and localStorage access issues
 */
export function useAuth() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  const checkAuthStatus = () => {
    try {
      const token = localStorage.getItem('certalert_jwt');
      const userId = localStorage.getItem('certalert_user_id');
      
      const loggedIn = !!token;
      setIsLoggedIn(loggedIn);
      
      if (loggedIn && userId) {
        setUser({ id: userId, token });
      } else {
        setUser(null);
      }
    } catch (error) {
      console.warn('Failed to access localStorage:', error);
      setIsLoggedIn(false);
      setUser(null);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    checkAuthStatus();

    // Listen for storage changes (when user logs in/out in another tab)
    const handleStorageChange = (e) => {
      if (e.key === 'certalert_jwt' || e.key === 'certalert_user_id') {
        checkAuthStatus();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = (token, userId) => {
    try {
      localStorage.setItem('certalert_jwt', token);
      if (userId) {
        localStorage.setItem('certalert_user_id', userId);
      }
      checkAuthStatus();
    } catch (error) {
      console.error('Failed to save authentication data:', error);
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem('certalert_jwt');
      localStorage.removeItem('certalert_user_id');
      setIsLoggedIn(false);
      setUser(null);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to clear authentication data:', error);
    }
  };

  return {
    isLoggedIn,
    isLoading,
    user,
    login,
    logout,
    checkAuthStatus
  };
}

/**
 * Simple hook that just returns the current token
 * Safe to use in API calls and components that need the token
 */
export function useAuthToken() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    try {
      const currentToken = localStorage.getItem('certalert_jwt');
      setToken(currentToken);
    } catch (error) {
      console.warn('Failed to get auth token:', error);
      setToken(null);
    }
  }, []);

  return token;
}