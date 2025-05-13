import React, { useState, useEffect, useContext } from 'react';
import api from '../utils/axiosConfig';
import { WishlistContext } from '../context/WishlistContext';

const MyWishlist = () => {
  const { wishlistItems, removeFromWishlist, moveToCart } = useContext(WishlistContext);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // The WishlistContext should already handle loading the wishlist items
    setLoading(false);
  }, []);

  const handleRemoveFromWishlist = async (productId) => {
    try {
      await removeFromWishlist(productId);
      setNotification({ message: 'Item removed from wishlist', type: 'success' });
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to remove item from wishlist', 
        type: 'error' 
      });
    }
  };

  const handleMoveToCart = async (productId) => {
    try {
      await moveToCart(productId);
      setNotification({ message: 'Item moved to cart', type: 'success' });
    } catch (error) {
      console.error('Error moving to cart:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to move item to cart', 
        type: 'error' 
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  return (
    <div>
      {notification.message && (
        <div
          className={`notification ${notification.type} p-4 mb-4 text-center rounded-md shadow-md ${
            notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {notification.message}
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-lg font-medium mb-4">Your Wishlist</h3>

        {wishlistItems.length === 0 ? (
          <div className="bg-gray-100 p-6 rounded text-center text-gray-600">
            <p className="mb-4">Your wishlist is empty.</p>
            <a href="/products" className="text-red-500 hover:text-red-700 font-medium">
              Browse Products
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {wishlistItems.map((item) => (
              <div key={item.id} className="border rounded overflow-hidden">
                <div className="p-4">
                  <div className="flex items-center justify-center h-40 bg-gray-100 mb-4">
                    {item.image_url ? (
                      <img 
                        src={item.image_url} 
                        alt={item.name} 
                        className="h-full object-contain"
                      />
                    ) : (
                      <div className="text-gray-400">No image available</div>
                    )}
                  </div>
                  
                  <h4 className="font-medium mb-1">{item.name}</h4>
                  <div className="text-red-500 font-medium mb-3">KES{parseFloat(item.price).toFixed(2)}</div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleMoveToCart(item.id)}
                      className="flex-1 bg-red-500 hover:bg-red-600 text-white py-1 px-2 rounded text-sm"
                    >
                      Add to Cart
                    </button>
                    <button
                      onClick={() => handleRemoveFromWishlist(item.id)}
                      className="border border-gray-300 hover:bg-gray-100 text-gray-700 py-1 px-2 rounded text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyWishlist;
