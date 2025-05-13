import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { AuthContext } from './AuthContext';
import api from '../utils/axiosConfig';
import { SERVICE_ENDPOINTS } from '../utils/apiConfig';

export const CartContext = createContext();

const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cartTotal, setCartTotal] = useState(0);
  const { isAuthenticated, user } = useContext(AuthContext);

  // Calculate cart total
  const calculateTotal = useCallback((items) => {
    const total = items.reduce((sum, item) => {
      // Ensure price is a number by using parseFloat and handling NaN
      const price = parseFloat(item.price) || 0;
      // Ensure quantity is a number by using parseInt and handling NaN
      const quantity = parseInt(item.quantity, 10) || 0;
      return sum + (price * quantity);
    }, 0);
    setCartTotal(total);
  }, []);
  
  // Save cart to local storage
  const saveCartToLocalStorage = useCallback((items) => {
    localStorage.setItem('cart', JSON.stringify(items));
  }, []);
  
  // Load cart from local storage
  const loadCartFromLocalStorage = useCallback(() => {
    const storedCart = localStorage.getItem('cart');
    if (storedCart) {
      try {
        return JSON.parse(storedCart);
      } catch (error) {
        console.error('Error parsing cart from local storage:', error);
        return [];
      }
    }
    return [];
  }, []);

  // Cache for cart items to avoid redundant API calls
  const [cartCache, setCartCache] = useState({
    data: null,
    timestamp: null,
    expiryTime: 2 * 60 * 1000 // 2 minutes cache validity
  });

  // Fetch cart items
  const fetchCartItems = async (forceRefresh = false) => {
    // For non-authenticated users, always use local storage
    if (!isAuthenticated()) {
      console.log('User not authenticated, loading cart from local storage');
      return loadCartFromLocalStorage();
    }
    
    // Return cached data if available and not expired
    const now = Date.now();
    if (!forceRefresh && 
        cartCache.data && 
        cartCache.timestamp && 
        (now - cartCache.timestamp < cartCache.expiryTime)) {
      console.log('Using cached cart items');
      return cartCache.data;
    }
    
    try {      
      const response = await api.get('/cart');
      
      // Update cache
      setCartCache({
        data: response.data,
        timestamp: now,
        expiryTime: 2 * 60 * 1000
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching cart items:', error);
      return loadCartFromLocalStorage();
    }
  };

  // Update cart item quantity with optimistic update
  const updateCartItemQuantity = async (itemId, quantity) => {
    if (!isAuthenticated()) {
      // Update local storage cart
      const localCart = loadCartFromLocalStorage();
      const updatedCart = localCart.map(item => 
        item.item_id === itemId ? { ...item, quantity } : item
      );
      
      saveCartToLocalStorage(updatedCart);
      setCartItems(updatedCart);
      calculateTotal(updatedCart);
      return { success: true, cart: updatedCart };
    }
    
    try {
      // Optimistic update - update cart state immediately before API call
      if (cartCache.data) {
        const updatedCache = cartCache.data.map(item => 
          item.item_id === itemId ? { ...item, quantity } : item
        );
        
        setCartCache({
          ...cartCache,
          data: updatedCache,
          timestamp: Date.now()
        });
        
        setCartItems(updatedCache);
        calculateTotal(updatedCache);
      }
      
      const response = await api.post(`/cart/${itemId}`, { quantity });
      return response.data;
    } catch (error) {
      console.error('Error updating cart item:', error);
      // Revert optimistic update on error by refreshing
      await fetchCartItems(true);
      throw error;
    }
  };

  // Add to cart with optimistic update and debouncing
  const addToCart = async (productId, quantity = 1, productDetails = null) => {
    if (!isAuthenticated()) {
      // Add to local storage cart
      const localCart = loadCartFromLocalStorage();
      
      // Check if the item already exists in the cart
      const existingItemIndex = localCart.findIndex(item => 
        item.product_id === productId || item.id === productId
      );
      
      let updatedCart;
      
      if (existingItemIndex >= 0) {
        // Update quantity if item exists
        updatedCart = localCart.map((item, index) => 
          index === existingItemIndex 
            ? { ...item, quantity: parseInt(item.quantity, 10) + parseInt(quantity, 10) } 
            : item
        );
      } else {
        // Add new item if it doesn't exist
        // If we have product details, use them, otherwise create a minimal item
        const newItem = productDetails || {
          item_id: `local-${Date.now()}`,
          product_id: productId,
          id: productId,
          quantity: quantity,
          // These fields will be populated when product details are fetched
          name: "Product",
          price: 0,
          image_url: "/images/placeholder.png"
        };
        
        // Ensure the item has the correct structure
        const cartItem = {
          ...newItem,
          item_id: newItem.item_id || `local-${Date.now()}`,
          product_id: productId,
          quantity: quantity
        };
        
        updatedCart = [...localCart, cartItem];
      }
      
      saveCartToLocalStorage(updatedCart);
      setCartItems(updatedCart);
      calculateTotal(updatedCart);
      return { success: true, cart: updatedCart };
    }
    
    try {
      // Optimistic update for authenticated users
      if (cartCache.data) {
        let updatedCache;
        
        // Check if the item already exists in the cart
        const existingItem = cartCache.data.find(item => 
          item.product_id === productId || item.id === productId
        );
        
        if (existingItem) {
          // Update quantity if item exists
          updatedCache = cartCache.data.map(item => 
            (item.product_id === productId || item.id === productId)
              ? { ...item, quantity: parseInt(item.quantity, 10) + parseInt(quantity, 10) }
              : item
          );
        } else if (productDetails) {
          // Add new item with product details
          const cartItem = {
            ...productDetails,
            item_id: productDetails.item_id || `temp-${Date.now()}`,
            product_id: productId,
            quantity: quantity
          };
          updatedCache = [...cartCache.data, cartItem];
        }
        
        // Only update cache if we have enough information
        if (updatedCache) {
          setCartCache({
            ...cartCache,
            data: updatedCache,
            timestamp: Date.now()
          });
          
          setCartItems(updatedCache);
          calculateTotal(updatedCache);
        }
      }
      
      const response = await api.post('/cart', { product_id: productId, quantity });
      
      // Refresh cart data after adding item to ensure consistency
      const freshCartData = await fetchCartItems(true);
      setCartItems(freshCartData);
      calculateTotal(freshCartData);
      
      return response.data;
    } catch (error) {
      console.error('Error adding to cart:', error);
      // Revert optimistic update on error by refreshing
      await fetchCartItems(true);
      throw error;
    }
  };

  // Remove cart item with optimistic update
  const removeFromCart = async (itemId) => {
    if (!isAuthenticated()) {
      // Remove from local storage cart
      const localCart = loadCartFromLocalStorage();
      const updatedCart = localCart.filter(item => item.item_id !== itemId);
      
      saveCartToLocalStorage(updatedCart);
      setCartItems(updatedCart);
      calculateTotal(updatedCart);
      return { success: true, cart: updatedCart };
    }
    
    try {
      // Optimistic update - remove item from state immediately before API call
      if (cartCache.data) {
        const updatedCache = cartCache.data.filter(item => item.item_id !== itemId);
        
        setCartCache({
          ...cartCache,
          data: updatedCache,
          timestamp: Date.now()
        });
        
        setCartItems(updatedCache);
        calculateTotal(updatedCache);
      }
      
      const response = await api.delete(`/cart/${itemId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing from cart:', error);
      // Revert optimistic update on error by refreshing
      await fetchCartItems(true);
      throw error;
    }
  };

  // Clear cart
  const clearCart = useCallback(() => {
    setCartItems([]);
    setCartTotal(0);
    saveCartToLocalStorage([]);
  }, [saveCartToLocalStorage]);

  useEffect(() => {
    let isMounted = true;

    const initializeCart = async () => {
      if (isMounted) {
        try {
          setLoading(true);
          const data = await fetchCartItems();
          setCartItems(data);
          calculateTotal(data);
          setLoading(false);
        } catch (error) {
          setError(error.message);
          setLoading(false);
        }
      }
    };

    initializeCart();
    
    // Set up a refresh interval for authenticated users
    let refreshInterval;
    if (isAuthenticated()) {
      refreshInterval = setInterval(() => {
        if (isMounted) {
          // Refresh cart data in the background every 5 minutes
          fetchCartItems(true).then(data => {
            if (isMounted) {
              setCartItems(data);
              calculateTotal(data);
            }
          }).catch(err => console.error('Background cart refresh error:', err));
        }
      }, 5 * 60 * 1000); // 5 minutes
    }
    
    return () => {
      isMounted = false;
      if (refreshInterval) clearInterval(refreshInterval);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]); // Removed fetchCartItems from dependency array to prevent infinite loop
  
  // Sync cart with local storage when authenticated state changes
  useEffect(() => {
    const syncCartWithServer = async () => {
      if (isAuthenticated()) {
        // If user just logged in, we might want to merge their local cart with server cart
        const localCart = loadCartFromLocalStorage();
        
        if (localCart.length > 0) {
          // Use a debounced approach to prevent multiple rapid updates
          const syncPromises = [];
          
          // For each item in local cart, add to server cart
          for (const item of localCart) {
            try {
              // Collect all promises but don't await them individually
              syncPromises.push(
                addToCart(item.product_id || item.id, item.quantity)
                  .catch(error => console.error('Error syncing local cart item to server:', error))
              );
            } catch (error) {
              console.error('Error preparing to sync cart item:', error);
            }
          }
          
          // Wait for all sync operations to complete
          await Promise.allSettled(syncPromises);
          
          // Clear local cart after syncing
          saveCartToLocalStorage([]);
          
          // Fetch the updated cart from server
          const serverCart = await fetchCartItems(true); // Force refresh
          setCartItems(serverCart);
          calculateTotal(serverCart);
        }
      }
    };
    
    syncCartWithServer();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  // Check if a product is in the cart
  const isInCart = useCallback((productId) => {
    return cartItems.some(item => {
      // Check both id and product_id to handle different formats
      return (item.product_id === productId || item.id === productId);
    });
  }, [cartItems]);

  return (
    <CartContext.Provider value={{
      cartItems,
      cartTotal,
      loading,
      error,
      fetchCartItems,
      addToCart,
      updateCartItemQuantity,
      removeFromCart,
      clearCart,
      isInCart
    }}>
      {children}
    </CartContext.Provider>
  );
};

export default CartProvider;
