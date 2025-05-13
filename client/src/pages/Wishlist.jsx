import React, { useContext, useEffect, useState, useCallback, memo } from 'react';
import { Trash2, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { CartContext } from '../context/CartContext';
import { WishlistContext } from '../context/WishlistContext';

// Recommended items are now fetched dynamically from the WishlistContext

// Reusable Product Card component
// Memoized Product Card component to prevent unnecessary re-renders
const ProductCard = React.memo(({ item, isWishlistItem = false, onAction, actionText, actionIcon }) => {
  const { addToCart } = useContext(CartContext);
  
  // Handle image error
  const handleImageError = useCallback((e) => {
    e.target.src = '/images/placeholder.png';
    e.target.onerror = null;
  }, []);

  return (
    <div key={item.id || item.product_id} className="relative border p-4 group">
      {/* Badge displays (discount or new) */}
      {item.discount && (
        <div className="absolute top-2 left-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
          {item.discount}
        </div>
      )}
      {item.isNew && (
        <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded">
          NEW
        </div>
      )}
      
      {/* Action button (trash for wishlist items, eye for recommended) */}
      <button 
        onClick={() => isWishlistItem && onAction(item)}
        className={`absolute top-2 right-2 text-gray-500 ${isWishlistItem ? 'hover:text-red-500' : 'hover:text-black'} transition`}
      >
        {actionIcon}
      </button>
      
      {/* Product image */}
      <Link to={`/product/${item.product_id || item.id}`}>
        <img 
          src={item.image_url || item.image} 
          alt={item.name} 
          className="mx-auto h-36 object-contain" 
          onError={handleImageError}
        />
      </Link>
      
      {/* Product details */}
      <h3 className="mt-4 font-medium">{item.name}</h3>
      <div className="text-red-600 font-semibold">KES{item.price}</div>
      
      {/* Optional old price */}
      {item.oldPrice && (
        <div className="text-gray-500 line-through text-sm">KES{item.oldPrice}</div>
      )}
      
      {/* Optional rating */}
      {item.rating && (
        <div className="flex items-center gap-1 text-yellow-500 mt-1">
          {'★'.repeat(item.rating)} <span className="text-gray-600 text-sm">({item.rating})</span>
        </div>
      )}
      
      {/* Action button */}
      <button 
        onClick={() => isWishlistItem ? onAction(item) : addToCart(item.id)}
        className="w-full mt-3 bg-black text-white py-2 hover:bg-red-600 transition"
      >
        {actionText}
      </button>
    </div>
  );
});

const Wishlist = () => {
  const { addToCart } = useContext(CartContext);
  const { 
    wishlistItems, 
    recommendedItems,
    loading, 
    recommendedLoading,
    error, 
    recommendedError,
    fetchWishlistItems, 
    removeFromWishlist, 
    moveToCart, 
    moveAllToCart,
    fetchRecommendedItems
  } = useContext(WishlistContext);
  
  const [notification, setNotification] = useState({ message: '', type: '' });

  // Only fetch wishlist items on mount and when dependencies change
  useEffect(() => {
    fetchWishlistItems();
    // We don't need to check wishlistItems.length here as the WishlistContext
    // will handle fetching recommended items when wishlist changes
  }, [fetchWishlistItems]);

  // Memoize the notification setter to avoid creating new functions on each render
  const showNotification = useCallback((message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification({ message: '', type: '' }), 3000);
  }, []);

  const handleMoveToCart = useCallback(async (item) => {
    try {
      const result = await moveToCart(item.product_id);
      if (result.success) {
        showNotification(`${item.name} has been moved to the cart.`);
      } else {
        showNotification(result.error || 'Failed to move item to cart', 'error');
      }
    } catch (error) {
      console.error('Error moving item to cart:', error);
      showNotification(error.message || 'Failed to move item to cart', 'error');
    }
  }, [moveToCart, showNotification]);

  const handleRemoveFromWishlist = useCallback(async (item) => {
    try {
      const result = await removeFromWishlist(item.product_id);
      if (result.success) {
        showNotification(`${item.name} has been removed from your wishlist.`);
      } else {
        showNotification(result.error || 'Failed to remove item from wishlist', 'error');
      }
    } catch (error) {
      console.error('Error removing item from wishlist:', error);
      showNotification(error.message || 'Failed to remove item from wishlist', 'error');
    }
  }, [removeFromWishlist, showNotification]);

  const handleMoveAllToCart = useCallback(async () => {
    try {
      const result = await moveAllToCart();
      if (result.success) {
        showNotification('All items have been moved to your cart.');
      } else {
        showNotification(result.error || 'Failed to move all items to cart', 'error');
      }
    } catch (error) {
      console.error('Error moving all items to cart:', error);
      showNotification(error.message || 'Failed to move all items to cart', 'error');
    }
  }, [moveAllToCart, showNotification]);

  // Render empty wishlist message
  const renderEmptyWishlist = () => (
    <div className="col-span-full text-center py-8">
      <p className="mb-4">Your wishlist is empty.</p>
      <Link to="/" className="px-4 py-2 bg-black text-white hover:bg-red-600 transition">
        Continue Shopping
      </Link>
    </div>
  );

  return (
    <div className="px-6 md:px-12 py-10 space-y-12 relative">
      {/* Notification */}
      {notification.message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded shadow-lg ${notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {notification.message}
        </div>
      )}
      {/* Wishlist Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold">Wishlist ({wishlistItems.length})</h2>
        {wishlistItems.length > 0 && (
          <button 
            onClick={handleMoveAllToCart}
            className="px-4 py-2 border border-black hover:bg-black hover:text-white transition"
          >
            Move All To Bag
          </button>
        )}
      </div>

      {/* Wishlist Items */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {loading ? (
          <div className="col-span-full text-center py-8">Loading wishlist items...</div>
        ) : error ? (
          <div className="col-span-full text-center py-8 text-red-500">{error}</div>
        ) : wishlistItems.length === 0 ? (
          renderEmptyWishlist()
        ) : (
          wishlistItems.map(item => (
            <ProductCard 
              key={item.product_id}
              item={item} 
              isWishlistItem={true}
              onAction={handleMoveToCart}
              actionText="Move To Cart"
              actionIcon={<Trash2 size={16} onClick={(e) => {
                e.stopPropagation();
                handleRemoveFromWishlist(item);
              }} />}
            />
          ))
        )}
      </div>

      {/* Just For You - Only show if wishlist has items */}
      {wishlistItems.length > 0 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-red-600">Just For You</h2>
            <Link to="/" className="px-4 py-2 border border-black hover:bg-black hover:text-white transition">
              See All
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {recommendedLoading ? (
              <div className="col-span-full text-center py-8">Loading recommended items...</div>
            ) : recommendedError ? (
              <div className="col-span-full text-center py-8 text-red-500">{recommendedError}</div>
            ) : recommendedItems.length === 0 ? (
              <div className="col-span-full text-center py-8">No recommendations available.</div>
            ) : (
              recommendedItems.map(item => (
                <ProductCard 
                  key={item.id || item.product_id}
                  item={item} 
                  actionText="Add To Cart"
                  actionIcon={<Eye size={16} />}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Wishlist;
