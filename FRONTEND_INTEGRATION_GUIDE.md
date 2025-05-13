# Shop-meetingAPI Frontend Integration Guide

## Overview

This document outlines a recommended frontend architecture that will seamlessly integrate with the Shop-meetingAPI microservices backend. It provides detailed guidance on component structure, state management, and API service integration.

## Frontend Architecture

### Recommended Technology Stack

- **Framework**: React
- **State Management**: Redux Toolkit
- **Routing**: React Router
- **API Calls**: Axios (with interceptors for auth)
- **Form Handling**: Formik + Yup
- **UI Components**: Material UI or Tailwind CSS
- **Testing**: Jest + React Testing Library

### Project Structure

```
src/
├── api/                 # API service integrations
│   ├── axios.js         # Axios instance with interceptors
│   ├── authApi.js       # Auth service endpoints
│   ├── profileApi.js    # Profile service endpoints
│   ├── productApi.js    # Product service endpoints
│   ├── cartApi.js       # Cart service endpoints
│   ├── orderApi.js      # Order service endpoints
│   └── supportApi.js    # Customer support endpoints
├── components/          # Reusable UI components
│   ├── common/          # Common UI elements
│   ├── layout/          # Layout components
│   ├── auth/            # Authentication components
│   ├── products/        # Product-related components
│   ├── cart/            # Shopping cart components
│   ├── checkout/        # Checkout components
│   ├── profile/         # User profile components
│   ├── orders/          # Order management components
│   └── support/         # Customer support components
├── hooks/               # Custom React hooks
├── pages/               # Page components
├── redux/               # Redux state management
│   ├── slices/          # Redux toolkit slices
│   └── store.js         # Redux store configuration
├── routes/              # Routing configuration
├── utils/               # Utility functions
├── App.js               # Main application component
└── index.js             # Application entry point
```

## Service Integration Details

### 1. Auth Service Integration

#### API Service (`api/authApi.js`)

```javascript
import api from './axios';

export const authApi = {
  register: (userData) => api.post('/api/v1/auth/register', userData),
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  logout: () => api.post('/api/v1/auth/logout'),
  checkAuthStatus: () => api.get('/api/v1/auth/status'),
  resetPassword: (email) => api.post('/api/v1/auth/reset-password', { email }),
  changePassword: (data) => api.post('/api/v1/auth/change-password', data)
};
```

#### Redux Slice (`redux/slices/authSlice.js`)

```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authApi } from '../../api/authApi';

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data.error || 'Login failed');
    }
  }
);

// Other auth-related async thunks (register, logout, etc.)

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null
  },
  reducers: {
    // Synchronous reducers
  },
  extraReducers: (builder) => {
    // Handle async actions
  }
});

export default authSlice.reducer;
```

#### Components

- `components/auth/LoginForm.jsx`: Form for user login
- `components/auth/RegisterForm.jsx`: Form for new user registration
- `components/auth/PasswordReset.jsx`: Password reset functionality
- `pages/Login.jsx`: Login page
- `pages/Register.jsx`: Registration page
- `hooks/useAuth.js`: Custom hook for auth-related functionality

### 2. Profile Service Integration

#### API Service (`api/profileApi.js`)

```javascript
import api from './axios';

export const profileApi = {
  getProfile: (userId) => api.get(`/api/v1/profiles/${userId}`),
  updateProfile: (userId, profileData) => api.put(`/api/v1/profiles/${userId}`, profileData),
  addAddress: (addressData) => api.post('/api/v1/profiles/addresses', addressData),
  updateAddress: (addressId, addressData) => api.put(`/api/v1/profiles/addresses/${addressId}`, addressData),
  deleteAddress: (addressId) => api.delete(`/api/v1/profiles/addresses/${addressId}`),
  getAddresses: () => api.get('/api/v1/profiles/addresses')
};
```

#### Components

- `components/profile/ProfileForm.jsx`: Form for updating user profile information
- `components/profile/AddressForm.jsx`: Form for adding/editing addresses
- `components/profile/AddressList.jsx`: List of user addresses
- `pages/Profile.jsx`: User profile management page

### 3. Product Service Integration

#### API Service (`api/productApi.js`)

```javascript
import api from './axios';

export const productApi = {
  getProducts: (page = 1, filters = {}) => api.get('/api/v1/products', { params: { page, ...filters } }),
  getProduct: (productId) => api.get(`/api/v1/products/${productId}`),
  searchProducts: (query) => api.get('/api/v1/products/search', { params: { q: query } }),
  getCategories: () => api.get('/api/v1/products/categories'),
  getRecommendations: () => api.get('/api/v1/products/recommendations')
};
```

#### Components

- `components/products/ProductList.jsx`: Grid/list of product cards
- `components/products/ProductCard.jsx`: Individual product display card
- `components/products/ProductDetail.jsx`: Detailed product view
- `components/products/ProductSearch.jsx`: Search and filter functionality
- `components/products/CategoryFilter.jsx`: Category-based filtering
- `pages/ProductListing.jsx`: Main product browsing page
- `pages/ProductDetail.jsx`: Individual product page

### 4. Cart Service Integration

#### API Service (`api/cartApi.js`)

```javascript
import api from './axios';

export const cartApi = {
  getCart: () => api.get('/api/v1/carts'),
  addToCart: (productId, quantity = 1) => api.post('/api/v1/carts/items', { product_id: productId, quantity }),
  updateCartItem: (itemId, quantity) => api.put(`/api/v1/carts/items/${itemId}`, { quantity }),
  removeFromCart: (itemId) => api.delete(`/api/v1/carts/items/${itemId}`),
  clearCart: () => api.delete('/api/v1/carts')
};
```

#### Redux Slice (`redux/slices/cartSlice.js`)

```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { cartApi } from '../../api/cartApi';

export const fetchCart = createAsyncThunk(
  'cart/fetchCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartApi.getCart();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data.error || 'Failed to fetch cart');
    }
  }
);

export const addToCart = createAsyncThunk(
  'cart/addToCart',
  async ({ productId, quantity }, { rejectWithValue }) => {
    try {
      const response = await cartApi.addToCart(productId, quantity);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data.error || 'Failed to add item to cart');
    }
  }
);

// Other cart operations as thunks

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    total: 0,
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    // Handle async actions
  }
});

export default cartSlice.reducer;
```

#### Components

- `components/cart/CartItem.jsx`: Individual cart item display
- `components/cart/CartList.jsx`: List of items in cart
- `components/cart/CartSummary.jsx`: Cart total and checkout button
- `components/cart/AddToCartButton.jsx`: Button for adding items to cart
- `pages/Cart.jsx`: Shopping cart page

### 5. Order Service Integration

#### API Service (`api/orderApi.js`)

```javascript
import api from './axios';

export const orderApi = {
  createOrder: (orderData) => api.post('/api/v1/orders', orderData),
  getOrders: (page = 1) => api.get('/api/v1/orders', { params: { page } }),
  getOrder: (orderId) => api.get(`/api/v1/orders/${orderId}`),
  cancelOrder: (orderId) => api.post(`/api/v1/orders/${orderId}/cancel`),
  trackOrder: (orderId) => api.get(`/api/v1/orders/${orderId}/tracking`)
};
```

#### Components

- `components/checkout/CheckoutForm.jsx`: Order placement form
- `components/checkout/PaymentMethod.jsx`: Payment method selection
- `components/checkout/ShippingAddress.jsx`: Shipping address selection/entry
- `components/orders/OrderList.jsx`: List of user's orders
- `components/orders/OrderDetail.jsx`: Detailed view of a specific order
- `components/orders/OrderTracking.jsx`: Order tracking information
- `pages/Checkout.jsx`: Checkout process page
- `pages/OrderHistory.jsx`: Order history listing page
- `pages/OrderDetail.jsx`: Single order details page

### 6. Customer Support Service Integration

#### API Service (`api/supportApi.js`)

```javascript
import api from './axios';

export const supportApi = {
  getTickets: () => api.get('/api/v1/tickets'),
  getTicket: (ticketId) => api.get(`/api/v1/tickets/${ticketId}`),
  createTicket: (ticketData) => api.post('/api/v1/tickets', ticketData),
  updateTicket: (ticketId, ticketData) => api.put(`/api/v1/tickets/${ticketId}`, ticketData),
  closeTicket: (ticketId) => api.post(`/api/v1/tickets/${ticketId}/close`),
  addMessage: (ticketId, message) => api.post(`/api/v1/tickets/${ticketId}/messages`, { message })
};
```

#### WebSocket Integration for Live Chat

```javascript
// hooks/useSupportChat.js
import { useState, useEffect, useCallback } from 'react';

export const useSupportChat = (ticketId) => {
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!ticketId) return;
    
    const ws = new WebSocket(`ws://localhost:8080/api/v1/tickets/${ticketId}/chat`);
    
    ws.onopen = () => {
      setConnected(true);
      ws.send(JSON.stringify({ type: 'auth', token }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };
    
    ws.onclose = () => {
      setConnected(false);
    };
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, [ticketId, token]);
  
  const sendMessage = useCallback((content) => {
    if (socket && connected) {
      socket.send(JSON.stringify({
        type: 'message',
        content,
        timestamp: new Date().toISOString()
      }));
    }
  }, [socket, connected]);
  
  return { messages, sendMessage, connected };
};
```

#### Components

- `components/support/TicketForm.jsx`: Form for creating support tickets
- `components/support/TicketList.jsx`: List of user's tickets
- `components/support/TicketDetail.jsx`: Detailed view of a specific ticket
- `components/support/ChatWindow.jsx`: Real-time chat interface
- `pages/Support.jsx`: Support center home page
- `pages/TicketDetail.jsx`: Specific ticket detail and chat page

## Axios Configuration with Auth Interceptors

```javascript
// api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor for handling authentication errors
api.interceptors.response.use(
  response => response,
  error => {
    // Handle 401 Unauthorized errors (token expired)
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Protected Routes Implementation

```javascript
// components/common/ProtectedRoute.jsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useSelector(state => state.auth);
  const location = useLocation();

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login but save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
```

## Routing Configuration

```javascript
// routes/index.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/common/ProtectedRoute';

// Auth pages
import Login from '../pages/Login';
import Register from '../pages/Register';
import ForgotPassword from '../pages/ForgotPassword';

// Public pages
import Home from '../pages/Home';
import ProductListing from '../pages/ProductListing';
import ProductDetail from '../pages/ProductDetail';

// Protected pages
import Profile from '../pages/Profile';
import Cart from '../pages/Cart';
import Checkout from '../pages/Checkout';
import OrderHistory from '../pages/OrderHistory';
import OrderDetail from '../pages/OrderDetail';
import Support from '../pages/Support';
import TicketDetail from '../pages/TicketDetail';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/products" element={<ProductListing />} />
      <Route path="/products/:productId" element={<ProductDetail />} />
      
      {/* Protected routes */}
      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      } />
      <Route path="/cart" element={
        <ProtectedRoute>
          <Cart />
        </ProtectedRoute>
      } />
      <Route path="/checkout" element={
        <ProtectedRoute>
          <Checkout />
        </ProtectedRoute>
      } />
      <Route path="/orders" element={
        <ProtectedRoute>
          <OrderHistory />
        </ProtectedRoute>
      } />
      <Route path="/orders/:orderId" element={
        <ProtectedRoute>
          <OrderDetail />
        </ProtectedRoute>
      } />
      <Route path="/support" element={
        <ProtectedRoute>
          <Support />
        </ProtectedRoute>
      } />
      <Route path="/support/tickets/:ticketId" element={
        <ProtectedRoute>
          <TicketDetail />
        </ProtectedRoute>
      } />
    </Routes>
  );
};

export default AppRoutes;
```

## Redux Store Configuration

```javascript
// redux/store.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import profileReducer from './slices/profileSlice';
import productReducer from './slices/productSlice';
import cartReducer from './slices/cartSlice';
import orderReducer from './slices/orderSlice';
import supportReducer from './slices/supportSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    profile: profileReducer,
    products: productReducer,
    cart: cartReducer,
    orders: orderReducer,
    support: supportReducer
  }
});

export default store;
```

## Error Handling Strategy

```javascript
// hooks/useApiError.js
import { useState, useCallback } from 'react';

export const useApiError = () => {
  const [error, setError] = useState(null);

  const handleError = useCallback((err) => {
    if (err.response) {
      // The request was made and the server responded with an error status
      const serverError = err.response.data.error || {
        code: `HTTP_${err.response.status}`,
        message: 'An error occurred while processing your request'
      };
      setError(serverError);
    } else if (err.request) {
      // The request was made but no response was received
      setError({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to the server. Please check your internet connection.'
      });
    } else {
      // Something happened in setting up the request
      setError({
        code: 'REQUEST_ERROR',
        message: err.message || 'An unexpected error occurred'
      });
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
};
```

## Environment Configuration

```javascript
// .env.development
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=ws://localhost:8080

// .env.production
REACT_APP_API_URL=https://api.your-production-domain.com
REACT_APP_WS_URL=wss://api.your-production-domain.com
```

## Implementation Recommendations

1. **State Management Approach**: Use Redux for global state (auth, cart) and React Context for localized state.

2. **Component Reusability**: Create a design system with common components (buttons, inputs, cards) for consistent UI.

3. **API Service Pattern**: Keep all API calls in dedicated service files, not in components or Redux actions.

4. **Authentication Flow**: Implement token refresh mechanisms for extended user sessions.

5. **Error Handling**: Use global error handlers for API errors with user-friendly messages.

6. **Form Validation**: Implement client-side validation before submitting to API endpoints.

7. **Responsive Design**: Build with mobile-first approach for all components.

8. **Loading States**: Implement skeletal loading for better user experience during API calls.

9. **Code Splitting**: Use React.lazy() for route-based code splitting to improve initial load time.

10. **Testing Strategy**: Test components in isolation with Jest and React Testing Library.

## Deployment Considerations

1. **Build Optimization**: Configure Webpack optimization for production builds.

2. **Environment Variables**: Use environment-specific variables for API endpoints.

3. **CORS Configuration**: Ensure your API allows requests from your frontend domain.

4. **SSL/TLS**: Deploy with HTTPS for secure communication.

5. **CDN Integration**: Use a CDN for static assets (images, bundled JS/CSS).

6. **Performance Monitoring**: Implement tools like Google Analytics and Sentry for monitoring.

## Getting Started

1. Create a new React application:
   ```bash
   npx create-react-app shop-meeting-frontend
   cd shop-meeting-frontend
   ```

2. Install required dependencies:
   ```bash
   npm install react-router-dom axios @reduxjs/toolkit react-redux formik yup @material-ui/core
   ```

3. Structure the project as outlined above.

4. Configure the API connection to point to your Shop-meetingAPI backend.

5. Implement the core authentication flow and routing.

6. Start building feature modules for each service integration.
