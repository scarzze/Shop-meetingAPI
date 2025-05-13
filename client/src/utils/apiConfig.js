// Central configuration for API URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Service endpoints
export const SERVICE_ENDPOINTS = {
  AUTH: '/auth',
  PROFILE: '/profile',
  PRODUCTS: '/products',
  CATEGORIES: '/categories',
  SEARCH: '/search',
  CART: '/cart',
  ORDERS: '/orders',
  TICKETS: '/tickets',
  FAVORITES: '/favorites'
};

export default API_URL;
