import { createContext, useState, useEffect, useContext, useCallback } from 'react';
import api from '../utils/axiosConfig';
import { SERVICE_ENDPOINTS } from '../utils/apiConfig';

// Create the auth context
export const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  // Initialize user state from localStorage if available
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        return JSON.parse(savedUser);
      } catch (e) {
        return null;
      }
    }
    return null;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to check authentication status
  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Check if we have a token in localStorage
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setUser(null);
        return false;
      }
      
      // Get user profile using the token
      const response = await api.get(`${SERVICE_ENDPOINTS.PROFILE}`);
      
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      return true;
    } catch (err) {
      // Clear user state and tokens if not authenticated
      setUser(null);
      
      // Only clear tokens if it's an authentication error (401)
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
      
      setError(err.message || err.response?.data?.error || 'Authentication failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Check if user is authenticated on component mount and set up token refresh
  useEffect(() => {
    // Initial auth check
    checkAuthStatus();

    // Set up token refresh interval (every 30 minutes)
    const refreshInterval = setInterval(async () => {
      if (user) {
        try {
          await refreshToken();
          console.log('Token refreshed successfully');
        } catch (err) {
          console.error('Failed to refresh token:', err);
        }
      }
    }, 30 * 60 * 1000); // 30 minutes
    
    // Set up event listener for auth:logout events
    const handleLogout = (event) => {
      logout();
      console.log(`Logged out due to: ${event.detail?.reason || 'user action'}`);
    };
    
    window.addEventListener('auth:logout', handleLogout);

    return () => {
      clearInterval(refreshInterval);
      window.removeEventListener('auth:logout', handleLogout);
    };
  }, []); // Empty dependency array to only run on mount

  // Login function
  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post(`${SERVICE_ENDPOINTS.AUTH}/login`, { username, password });
      
      // Store user data
      setUser(response.data.user);
      
      // Store tokens and user data in localStorage
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = useCallback(async () => {
    try {
      setLoading(true);
      
      // Try to call logout endpoint, but don't wait for it to complete
      // This ensures we still logout even if the server is unreachable
      api.post(`${SERVICE_ENDPOINTS.AUTH}/logout`, {}).catch(err => {
        console.error('Error during logout API call:', err);
      });
      
      // Clear user data and tokens immediately
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      return { success: true };
    } catch (err) {
      // Still clear local data even if API call fails
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      setError(err.message || err.response?.data?.error || 'Logout failed');
      return { success: true }; // Return success anyway since we've cleared local data
    } finally {
      setLoading(false);
    }
  }, []);

  // Refresh token function
  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      
      if (!refreshTokenValue) {
        throw new Error('No refresh token available');
      }
      
      // The token will be added by the interceptor
      const response = await api.post(`${SERVICE_ENDPOINTS.AUTH}/refresh`, { refresh_token: refreshTokenValue });
      
      // Update tokens in localStorage
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
      }
      
      return { success: true };
    } catch (err) {
      // Only logout if it's an authentication error, not if it's a network error
      if (err.response?.status === 401) {
        // If refresh fails due to invalid token, logout the user
        setUser(null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
      
      return { 
        success: false, 
        error: err.message || err.response?.data?.error || 'Token refresh failed',
        status: err.response?.status
      };
    }
  };

  // Check if user is authenticated
  const isAuthenticated = () => !!user || !!localStorage.getItem('access_token');

  // Email verification functions removed

  // Context value
  const value = {
    user,
    loading,
    error,
    login,
    logout,
    refreshToken,
    isAuthenticated,
    checkAuthStatus
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
