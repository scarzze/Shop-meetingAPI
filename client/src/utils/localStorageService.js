/**
 * Local Storage Service
 * 
 * This utility provides methods for managing local storage data for users
 * who haven't created an account yet or aren't logged in.
 */

// Maximum number of recently viewed products to store
const MAX_RECENT_PRODUCTS = 10;

/**
 * Save data to local storage
 * @param {string} key - Storage key
 * @param {any} data - Data to store
 */
export const saveToLocalStorage = (key, data) => {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.error(`Error saving ${key} to local storage:`, error);
  }
};

/**
 * Load data from local storage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key doesn't exist
 * @returns {any} - Parsed data or default value
 */
export const loadFromLocalStorage = (key, defaultValue = null) => {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : defaultValue;
  } catch (error) {
    console.error(`Error loading ${key} from local storage:`, error);
    return defaultValue;
  }
};

/**
 * Remove data from local storage
 * @param {string} key - Storage key to remove
 */
export const removeFromLocalStorage = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Error removing ${key} from local storage:`, error);
  }
};

/**
 * Add a product to recently viewed list
 * @param {Object} product - Product to add to recently viewed
 */
export const addToRecentlyViewed = (product) => {
  try {
    // Get current recently viewed products
    const recentlyViewed = loadFromLocalStorage('recentlyViewed', []);
    
    // Check if product already exists in the list
    const existingIndex = recentlyViewed.findIndex(item => 
      item.id === product.id || item.product_id === product.product_id
    );
    
    // If product exists, remove it (to add it to the beginning)
    if (existingIndex !== -1) {
      recentlyViewed.splice(existingIndex, 1);
    }
    
    // Add product to the beginning of the array
    recentlyViewed.unshift({
      ...product,
      viewedAt: new Date().toISOString()
    });
    
    // Limit the number of recently viewed products
    const limitedRecentlyViewed = recentlyViewed.slice(0, MAX_RECENT_PRODUCTS);
    
    // Save back to local storage
    saveToLocalStorage('recentlyViewed', limitedRecentlyViewed);
    
    return limitedRecentlyViewed;
  } catch (error) {
    console.error('Error adding to recently viewed:', error);
    return [];
  }
};

/**
 * Get recently viewed products
 * @returns {Array} - Recently viewed products
 */
export const getRecentlyViewed = () => {
  return loadFromLocalStorage('recentlyViewed', []);
};

/**
 * Clear all local storage data
 */
export const clearAllLocalStorage = () => {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('Error clearing local storage:', error);
  }
};

/**
 * Merge local storage cart with server cart after login
 * @param {Function} serverAddToCart - Function to add item to server cart
 * @returns {Promise<boolean>} - Success status
 */
export const mergeLocalCartWithServer = async (serverAddToCart) => {
  try {
    const localCart = loadFromLocalStorage('cart', []);
    
    if (localCart.length === 0) {
      return true;
    }
    
    // Add each local cart item to server
    for (const item of localCart) {
      await serverAddToCart(item.product_id || item.id, item.quantity);
    }
    
    // Clear local cart after sync
    removeFromLocalStorage('cart');
    return true;
  } catch (error) {
    console.error('Error merging local cart with server:', error);
    return false;
  }
};

/**
 * Merge local storage wishlist with server wishlist after login
 * @param {Function} serverAddToWishlist - Function to add item to server wishlist
 * @returns {Promise<boolean>} - Success status
 */
export const mergeLocalWishlistWithServer = async (serverAddToWishlist) => {
  try {
    const localWishlist = loadFromLocalStorage('wishlist', []);
    
    if (localWishlist.length === 0) {
      return true;
    }
    
    // Add each local wishlist item to server
    for (const item of localWishlist) {
      await serverAddToWishlist(item.product_id || item.id);
    }
    
    // Clear local wishlist after sync
    removeFromLocalStorage('wishlist');
    return true;
  } catch (error) {
    console.error('Error merging local wishlist with server:', error);
    return false;
  }
};
