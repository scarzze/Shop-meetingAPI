import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { CartContext } from './CartContext';
import { AuthContext } from './AuthContext';
import api from '../utils/axiosConfig';

export const WishlistContext = createContext();

const WishlistProvider = ({ children }) => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [recommendedItems, setRecommendedItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recommendedLoading, setRecommendedLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendedError, setRecommendedError] = useState(null);
  const { isAuthenticated, user } = useContext(AuthContext);
  const { addToCart } = useContext(CartContext);
  
  // Save wishlist to local storage
  const saveWishlistToLocalStorage = useCallback((items) => {
    localStorage.setItem('wishlist', JSON.stringify(items));
  }, []);
  
  // Load wishlist from local storage
  const loadWishlistFromLocalStorage = useCallback(() => {
    const storedWishlist = localStorage.getItem('wishlist');
    if (storedWishlist) {
      try {
        return JSON.parse(storedWishlist);
      } catch (error) {
        console.error('Error parsing wishlist from local storage:', error);
        return [];
      }
    }
    return [];
  }, []);

  // Cache for wishlist items to avoid redundant API calls
  const [wishlistCache, setWishlistCache] = useState({
    data: null,
    timestamp: null,
    expiryTime: 2 * 60 * 1000 // 2 minutes cache validity
  });

  // Fetch wishlist items
  const fetchWishlistItems = useCallback(async (forceRefresh = false) => {
    // For non-authenticated users, always use local storage
    if (!isAuthenticated()) {
      console.log('User not authenticated, loading wishlist from local storage');
      const localWishlist = loadWishlistFromLocalStorage();
      setWishlistItems(localWishlist);
      return localWishlist;
    }
    
    // Return cached data if available and not expired
    const now = Date.now();
    if (!forceRefresh && 
        wishlistCache.data && 
        wishlistCache.timestamp && 
        (now - wishlistCache.timestamp < wishlistCache.expiryTime)) {
      console.log('Using cached wishlist items');
      setWishlistItems(wishlistCache.data);
      return wishlistCache.data;
    }
    
    setLoading(true);
    try {
      const response = await api.get('/wishlist');
      const data = response.data;
      
      // Update cache
      setWishlistCache({
        data: data,
        timestamp: now,
        expiryTime: 2 * 60 * 1000
      });
      
      setWishlistItems(data);
      setLoading(false);
      return data;
    } catch (error) {
      console.error('Error fetching wishlist items:', error);
      setError('Failed to fetch wishlist items');
      setLoading(false);
      const localWishlist = loadWishlistFromLocalStorage();
      setWishlistItems(localWishlist);
      return localWishlist;
    }
  }, [isAuthenticated, loadWishlistFromLocalStorage, wishlistCache]);

  // Add to wishlist
  const addToWishlist = async (productId, productDetails = null) => {
    if (!isAuthenticated()) {
      // Add to local storage wishlist
      const localWishlist = loadWishlistFromLocalStorage();
      
      // Check if the item already exists in the wishlist
      const existingItem = localWishlist.find(item => 
        item.product_id === productId || item.id === productId
      );
      
      if (existingItem) {
        // Item already in wishlist, no need to add again
        return { success: true, wishlist: localWishlist };
      }
      
      // Add new item if it doesn't exist
      // If we have product details, use them, otherwise create a minimal item
      const newItem = productDetails || {
        id: productId,
        product_id: productId,
        // These fields will be populated when product details are fetched
        name: "Product",
        price: 0,
        image_url: "/images/placeholder.png"
      };
      
      const updatedWishlist = [...localWishlist, newItem];
      saveWishlistToLocalStorage(updatedWishlist);
      setWishlistItems(updatedWishlist);
      
      // Refresh recommendations after adding to wishlist
      fetchRecommendedItems(true);
      
      return { success: true, wishlist: updatedWishlist };
    }
    
    try {
      const response = await api.post('/wishlist', { product_id: productId });
      
      // Optimistic update to avoid full refresh
      if (wishlistCache.data) {
        // If we have product details, use them
        if (productDetails) {
          const updatedCache = [...wishlistCache.data, productDetails];
          setWishlistCache({
            ...wishlistCache,
            data: updatedCache,
            timestamp: Date.now()
          });
          setWishlistItems(updatedCache);
        } else {
          // Force refresh to get the updated data from server
          await fetchWishlistItems(true);
        }
      } else {
        await fetchWishlistItems(true);
      }
      
      // Refresh recommendations after adding to wishlist
      fetchRecommendedItems(true);
      
      return { success: true, wishlist: response.data };
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      setError('Failed to add item to wishlist');
      return { success: false, error: 'Failed to add item to wishlist' };
    }
  };

  // Remove from wishlist
  const removeFromWishlist = async (productId) => {
    if (!isAuthenticated()) {
      // Remove from local storage wishlist
      const localWishlist = loadWishlistFromLocalStorage();
      const updatedWishlist = localWishlist.filter(item => 
        item.product_id !== productId && item.id !== productId
      );
      
      saveWishlistToLocalStorage(updatedWishlist);
      setWishlistItems(updatedWishlist);
      
      // Refresh recommendations after removing from wishlist
      fetchRecommendedItems(true);
      
      return { success: true, wishlist: updatedWishlist };
    }
    
    try {
      await api.delete(`/wishlist/${productId}`);
      
      // Optimistic update to avoid full refresh
      if (wishlistCache.data) {
        const updatedCache = wishlistCache.data.filter(item => 
          item.product_id !== productId && item.id !== productId
        );
        setWishlistCache({
          ...wishlistCache,
          data: updatedCache,
          timestamp: Date.now()
        });
        setWishlistItems(updatedCache);
      } else {
        await fetchWishlistItems(true);
      }
      
      // Refresh recommendations after removing from wishlist
      fetchRecommendedItems(true);
      
      return { success: true };
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      setError('Failed to remove item from wishlist');
      return { success: false, error: 'Failed to remove item from wishlist' };
    }
  };

  // Check if an item is in the wishlist
  const isInWishlist = (productId) => {
    return wishlistItems.some(item => 
      item.product_id === productId || item.id === productId
    );
  };

  // Initialize wishlist
  useEffect(() => {
    fetchWishlistItems();
  }, [fetchWishlistItems, isAuthenticated]);

  // Sync wishlist with server when authentication state changes
  useEffect(() => {
    const syncWishlistWithServer = async () => {
      if (isAuthenticated()) {
        // If user just logged in, we might want to merge their local wishlist with server wishlist
        const localWishlist = loadWishlistFromLocalStorage();
        
        if (localWishlist.length > 0) {
          // For each item in local wishlist, add to server wishlist
          for (const item of localWishlist) {
            try {
              await addToWishlist(item.product_id || item.id);
            } catch (error) {
              console.error('Error syncing local wishlist item to server:', error);
            }
          }
          
          // Clear local wishlist after syncing
          saveWishlistToLocalStorage([]);
          
          // Fetch the updated wishlist from server
          await fetchWishlistItems();
        }
      }
    };
    
    syncWishlistWithServer();
  }, [isAuthenticated, addToWishlist, fetchWishlistItems, loadWishlistFromLocalStorage, saveWishlistToLocalStorage]);

  // Move item from wishlist to cart
  const moveToCart = async (productId) => {
    try {
      // Find the item in the wishlist
      const item = wishlistItems.find(item => item.product_id === productId);
      if (!item) {
        return { success: false, error: 'Item not found in wishlist' };
      }
      
      // Optimistic update - remove item from wishlist state immediately
      if (wishlistCache.data) {
        const updatedCache = wishlistCache.data.filter(item => 
          item.product_id !== productId && item.id !== productId
        );
        
        setWishlistCache({
          ...wishlistCache,
          data: updatedCache,
          timestamp: Date.now()
        });
        
        setWishlistItems(updatedCache);
      }
      
      // Add the item to the cart
      await addToCart(productId, 1, item);
      
      // Remove the item from the wishlist on the server
      if (isAuthenticated()) {
        await api.delete(`/wishlist/${productId}`);
      } else {
        // For non-authenticated users, update local storage
        const localWishlist = loadWishlistFromLocalStorage();
        const updatedWishlist = localWishlist.filter(item => 
          item.product_id !== productId && item.id !== productId
        );
        saveWishlistToLocalStorage(updatedWishlist);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Error moving item to cart:', error);
      setError('Failed to move item to cart');
      // Revert optimistic update on error by refreshing
      await fetchWishlistItems(true);
      return { success: false, error: 'Failed to move item to cart' };
    }
  };
  
  // Move all items from wishlist to cart
  const moveAllToCart = async () => {
    try {
      // Check if there are items in the wishlist
      if (wishlistItems.length === 0) {
        return { success: false, error: 'Wishlist is empty' };
      }
      
      // Optimistic update - clear wishlist state immediately
      setWishlistItems([]);
      setWishlistCache({
        data: [],
        timestamp: Date.now(),
        expiryTime: wishlistCache.expiryTime
      });
      
      // Store items for processing
      const itemsToProcess = [...wishlistItems];
      
      // Add each item to the cart in parallel
      const cartPromises = itemsToProcess.map(item => 
        addToCart(item.product_id, 1, item)
      );
      await Promise.all(cartPromises);
      
      // Clear the wishlist
      if (isAuthenticated()) {
        // Clear server wishlist in parallel
        const deletePromises = itemsToProcess.map(item => 
          api.delete(`/wishlist/${item.product_id}`)
        );
        await Promise.all(deletePromises);
      } else {
        // Clear local storage wishlist
        saveWishlistToLocalStorage([]);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Error moving all items to cart:', error);
      setError('Failed to move all items to cart');
      // Revert optimistic update on error by refreshing
      await fetchWishlistItems(true);
      return { success: false, error: 'Failed to move all items to cart' };
    }
  };

  // Cache for recommended products to avoid redundant API calls
  const [recommendedCache, setRecommendedCache] = useState({
    data: null,
    timestamp: null,
    expiryTime: 2 * 60 * 1000 // 2 minutes cache validity - shorter to get fresh recommendations
  });

  // Fetch recommended products based on user's wishlist and browsing history
  const fetchRecommendedItems = useCallback(async (forceRefresh = false) => {
    // Return cached data if available and not expired
    const now = Date.now();
    if (!forceRefresh && 
        recommendedCache.data && 
        recommendedCache.timestamp && 
        (now - recommendedCache.timestamp < recommendedCache.expiryTime)) {
      console.log('Using cached recommended items');
      setRecommendedItems(recommendedCache.data);
      return recommendedCache.data;
    }
    
    setRecommendedLoading(true);
    setRecommendedError(null);
    
    try {
      // Fetch personalized recommendations from the server
      const response = await api.get('/recommendations?limit=8');
      const data = response.data;
      
      // Update cache
      setRecommendedCache({
        data: data,
        timestamp: now,
        expiryTime: 2 * 60 * 1000 // 2 minutes cache validity
      });
      
      setRecommendedItems(data);
      setRecommendedLoading(false);
      return data;
    } catch (error) {
      console.error('Error fetching recommended items:', error);
      setRecommendedError('Failed to fetch recommended items');
      setRecommendedLoading(false);
      
      // Fallback to default recommended items if API fails
      const fallbackItems = [
        {
          id: 1,
          name: 'ASUS FHD Gaming Laptop',
          price: 9600,
          oldPrice: 11600,
          discount: '-35%',
          rating: 5,
          image_url: '/images/laptop.jpg'
        },
        {
          id: 2,
          name: 'Wireless Bluetooth Headphones',
          price: 1200,
          rating: 4,
          image_url: '/images/headphones.jpg'
        },
        {
          id: 3,
          name: 'Smart Watch Series 7',
          price: 3200,
          isNew: true,
          rating: 4,
          image_url: '/images/smartwatch.jpg'
        },
        {
          id: 4,
          name: 'Smartphone 13 Pro',
          price: 8500,
          rating: 5,
          image_url: '/images/smartphone.jpg'
        }
      ];
      
      setRecommendedItems(fallbackItems);
      return fallbackItems;
    }
  }, [recommendedCache]);

  // Fetch recommended items when wishlist changes, but with debounce
  useEffect(() => {
    let debounceTimer;
    
    if (wishlistItems.length > 0) {
      // Debounce the fetch to prevent multiple calls
      debounceTimer = setTimeout(() => {
        fetchRecommendedItems();
      }, 300); // 300ms debounce
    }
    
    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, [wishlistItems, fetchRecommendedItems]);

  return (
    <WishlistContext.Provider
      value={{
        wishlistItems,
        recommendedItems,
        loading,
        recommendedLoading,
        error,
        recommendedError,
        addToWishlist,
        removeFromWishlist,
        isInWishlist,
        fetchWishlistItems,
        moveToCart,
        moveAllToCart,
        fetchRecommendedItems
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
};

export default WishlistProvider;
