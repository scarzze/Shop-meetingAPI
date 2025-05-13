import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cloudinary } from '@cloudinary/url-gen';
import { fill } from '@cloudinary/url-gen/actions/resize';
import { FaHeart, FaRegHeart, FaShoppingCart, FaStar, FaStarHalfAlt, FaRegStar } from 'react-icons/fa';
import { WishlistContext } from '../context/WishlistContext';
import { CartContext } from '../context/CartContext';

const cld = new Cloudinary({
  cloud: {
    cloudName: 'dyzqn2sju',
  },
});

const getCloudinaryImageUrl = (publicId, width, height) => {
  // Check if the publicId is already a full URL
  if (publicId && publicId.startsWith('http')) {
    return publicId;
  }
  
  // Otherwise, generate a new URL using Cloudinary
  const image = cld.image(publicId);
  image.resize(fill().width(width).height(height));
  return image.toURL();
};

const ProductCard = ({ product, showPrice = true, showRatings = true }) => {
  const navigate = useNavigate();
  const { isInWishlist, addToWishlist, removeFromWishlist } = React.useContext(WishlistContext);
  const { addToCart } = React.useContext(CartContext);
  const [isHovered, setIsHovered] = React.useState(false);
  
  const handleProductClick = () => {
    navigate(`/product/${product.id}`);
    // Scroll to top of the page when navigating to product detail
    window.scrollTo(0, 0);
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    e.preventDefault();
    try {
      addToCart(product, 1);
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const handleWishlistToggle = (e) => {
    e.stopPropagation();
    e.preventDefault();
    try {
      if (isInWishlist && isInWishlist(product.id)) {
        removeFromWishlist(product.id);
      } else if (addToWishlist) {
        addToWishlist(product);
      }
    } catch (error) {
      console.error('Error toggling wishlist:', error);
    }
  };

  // Use image_url if available, fallback to image
  const productImage = product.image_url || product.image;
  
  // Calculate discount if both prices are available
  const discount = product.oldPrice && product.currentPrice 
    ? Math.round(((product.oldPrice - product.currentPrice) / product.oldPrice) * 100) 
    : null;
    
  // Generate star rating display
  const renderRatingStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(<FaStar key={i} className="text-yellow-400" />);
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(<FaStarHalfAlt key={i} className="text-yellow-400" />);
      } else {
        stars.push(<FaRegStar key={i} className="text-yellow-400" />);
      }
    }
    
    return stars;
  };

  return (
    <div 
      className="relative border p-4 rounded-lg shadow-sm hover:shadow-md transition cursor-pointer group" 
      onClick={handleProductClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Discount Badge */}
      {(product.discount || discount) && (
        <span className="absolute top-2 left-2 bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-full z-10">
          -{product.discount || discount}%
        </span>
      )}

      {/* Quick Action Buttons - Only visible on hover */}
      <div className={`absolute top-2 right-2 flex flex-col gap-2 transition-opacity duration-200 ${isHovered ? 'opacity-100' : 'opacity-0'}`}>
        <button 
          onClick={handleWishlistToggle}
          className="bg-white p-2 rounded-full shadow-md hover:bg-gray-100 transition-colors"
          aria-label="Add to wishlist"
        >
          {isInWishlist(product.id) ? 
            <FaHeart className="text-red-500" /> : 
            <FaRegHeart className="text-gray-600" />}
        </button>
        <button 
          onClick={handleAddToCart}
          className="bg-white p-2 rounded-full shadow-md hover:bg-gray-100 transition-colors"
          aria-label="Add to cart"
        >
          <FaShoppingCart className="text-gray-600" />
        </button>
      </div>

      {/* Image with hover effect */}
      <div className="relative overflow-hidden mb-3 group-hover:opacity-90 transition-opacity">
        <img
          src={productImage}
          alt={product.name}
          className="w-full h-48 object-contain transition-transform duration-300 group-hover:scale-105"
          onError={(e) => {
            e.target.src = '/images/placeholder.png'; // Fallback image
            e.target.onerror = null; // Prevent infinite loop
          }}
        />
      </div>

      {/* Product Info */}
      <div className="text-sm">
        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 h-10">{product.name}</h3>
        {showPrice && (
          <div className="flex items-center gap-2 mb-2">
            <span className="text-red-500 font-semibold">
              KES {(product.currentPrice || product.price || 0).toLocaleString()}
            </span>
            {product.oldPrice && (
              <span className="line-through text-gray-400 text-xs">KES {(parseInt(product.oldPrice) || 0).toLocaleString()}</span>
            )}
          </div>
        )}
        {showRatings && (
          <div className="flex items-center gap-1 mb-1">
            <div className="flex">
              {renderRatingStars(product.rating || 4)}
            </div>
            <span className="text-gray-500 text-xs">({typeof product.reviews === 'object' ? 0 : (product.reviews || 0)})</span>
          </div>
        )}
        
        {/* Category Tag */}
        {product.category && (
          <div className="mt-2">
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
              {product.category}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
