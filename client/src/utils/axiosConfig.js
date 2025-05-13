import axios from 'axios';
import API_URL from './apiConfig';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor to add Authorization header to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error.message);
      return Promise.reject({
        ...error,
        message: 'Network error. Please check your internet connection.'
      });
    }
    
    // If the error is 401 and we haven't already tried to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token available, redirect to login
          window.dispatchEvent(new CustomEvent('auth:logout', { detail: { reason: 'token_expired' } }));
          return Promise.reject({
            ...error,
            message: 'Authentication expired. Please log in again.'
          });
        }
        
        // Call the refresh endpoint
        const response = await axios.post(
          `${API_URL}/auth/refresh`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            },
            withCredentials: true
          }
        );
        
        // If successful, update the access token
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
          
          // Update the original request with the new token
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          
          // Retry the original request
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, clear tokens and trigger logout event
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new CustomEvent('auth:logout', { detail: { reason: 'refresh_failed' } }));
        return Promise.reject({
          ...error,
          message: 'Session expired. Please log in again.'
        });
      }
    }
    
    // Handle service unavailable errors (503)
    if (error.response?.status === 503) {
      return Promise.reject({
        ...error,
        message: 'Service temporarily unavailable. Please try again later.'
      });
    }
    
    // Handle not found errors (404)
    if (error.response?.status === 404) {
      return Promise.reject({
        ...error,
        message: 'Resource not found. Please check your request.'
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
