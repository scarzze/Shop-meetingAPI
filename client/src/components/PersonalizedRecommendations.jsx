import React, { useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaStar, FaRegHeart, FaHeart } from 'react-icons/fa';
import { WishlistContext } from '../context/WishlistContext';
import { AuthContext } from '../context/AuthContext';

const PersonalizedRecommendations = () => {
  const { 
    recommendedItems, 
    recommendedLoading, 
    recommendedError, 
    fetchRecommendedItems,
    addToWishlist,
    removeFromWishlist,
    isInWishlist
  } = useContext(WishlistContext);
  
  const { isAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    fetchRecommendedItems();
  }, [fetchRecommendedItems]);

  if (recommendedLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (recommendedError) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">{recommendedError}</p>
        <button 
          onClick={() => fetchRecommendedItems(true)} 
          className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Try Again
        </button>
      </div>
    );
  }

  const handleWishlistToggle = (e, product) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isInWishlist(product.id)) {
      removeFromWishlist(product.id);
    } else {
      addToWishlist(product.id, product);
    }
  };

  return (
    <section className="mt-16">
      <div className="flex justify-between items-center border-b pb-4">
        <div className="flex items-center">
          <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
          <h2 className="text-xl font-bold">Just For You</h2>
        </div>
        <h3 className="text-xl font-bold">
          {isAuthenticated() ? 'Personalized Picks' : 'Popular Products'}
        </h3>
        <div className="invisible">Spacer</div>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-6">
        {recommendedItems.slice(0, 8).map((product) => (
          <div key={product.id} className="group">
            <Link to={`/product/${product.id}`} className="block">
              <div className="bg-gray-100 rounded-lg p-4 relative overflow-hidden group">
                {/* Discount Tag */}
                {product.discount && (
                  <div className="absolute top-2 left-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                    {product.discount}
                  </div>
                )}
                
                {/* New Tag */}
                {product.isNew && (
                  <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded">
                    NEW
                  </div>
                )}
                
                {/* Wishlist Button */}
                <button 
                  onClick={(e) => handleWishlistToggle(e, product)}
                  className="absolute top-2 right-2 z-10 bg-white rounded-full p-2 shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  {isInWishlist(product.id) ? (
                    <FaHeart className="text-red-500" />
                  ) : (
                    <FaRegHeart className="text-gray-500 hover:text-red-500" />
                  )}
                </button>
                
                {/* Product Image */}
                <div className="h-48 flex items-center justify-center mb-4 overflow-hidden">
                  <img 
                    src={product.image_url} 
                    alt={product.name} 
                    className="h-full w-full object-contain transition-transform duration-300 group-hover:scale-110" 
                  />
                </div>
                
                {/* Product Info */}
                <div>
                  <h3 className="font-medium text-gray-800 line-clamp-2 h-12">{product.name}</h3>
                  <div className="flex items-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <FaStar 
                        key={i} 
                        className={i < product.rating ? "text-yellow-400" : "text-gray-300"} 
                        size={14} 
                      />
                    ))}
                  </div>
                  <div className="mt-2 flex items-center">
                    <span className="font-bold text-gray-800">${product.price}</span>
                    {product.oldPrice && (
                      <span className="ml-2 text-sm text-gray-500 line-through">${product.oldPrice}</span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
};

export default PersonalizedRecommendations;
