import React, { memo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaTrash } from 'react-icons/fa';
import { Cloudinary } from '@cloudinary/url-gen';
import { fill } from '@cloudinary/url-gen/actions/resize';

const cld = new Cloudinary({
  cloud: {
    cloudName: 'dyzqn2sju'
  }
});

const CartItem = memo(({ item, onQuantityChange, onRemove }) => {
  const [localQuantity, setLocalQuantity] = useState(item.quantity);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateTimeout, setUpdateTimeout] = useState(null);

  // Handle image URL
  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return '/images/placeholder.png';
    
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    
    const image = cld.image(imageUrl);
    image.resize(fill().width(80).height(80));
    return image.toURL();
  };

  // Debounced quantity update
  const handleQuantityChange = (change) => {
    const newQuantity = localQuantity + change;
    if (newQuantity >= 1) {
      setLocalQuantity(newQuantity);
      setIsUpdating(true);

      // Clear any existing timeout
      if (updateTimeout) {
        clearTimeout(updateTimeout);
      }

      // Set new timeout for debounced update
      const timeoutId = setTimeout(async () => {
        await onQuantityChange(item.item_id, newQuantity);
        setIsUpdating(false);
      }, 500); // Wait 500ms before sending update

      setUpdateTimeout(timeoutId);
    }
  };

  const handleRemove = () => {
    if (updateTimeout) {
      clearTimeout(updateTimeout);
    }
    onRemove(item.item_id);
  };

  // Calculate prices with proper type conversion
  const price = parseFloat(item.price);
  const subtotal = price * localQuantity;
  
  return (
    <div className="flex flex-col md:flex-row items-start md:items-center py-4 relative group">
      {/* Remove Button */}
      <button 
        onClick={handleRemove}
        className="text-red-500 mr-2 hover:text-red-700 transition absolute md:relative right-0 top-0 md:top-auto"
        aria-label="Remove item"
      >
        <FaTrash size={16} />
      </button>
      
      {/* Product Image */}
      <Link to={`/product/${item.product_id}`} className="w-20 h-20 flex-shrink-0">
        <img 
          src={getImageUrl(item.image_url)}
          alt={item.name}
          className="w-full h-full object-contain border rounded p-1"
          onError={(e) => {
            e.target.src = '/images/placeholder.png';
            e.target.onerror = null;
          }}
        />
      </Link>
      
      {/* Product Details */}
      <div className="flex-grow mx-4 mt-2 md:mt-0">
        <Link 
          to={`/product/${item.product_id}`}
          className="font-medium hover:text-red-500 transition line-clamp-2"
        >
          {item.name}
        </Link>
      </div>
      
      {/* Price */}
      <div className="w-24 text-right font-medium mt-2 md:mt-0">
        KES{price.toFixed(2)}
      </div>
      
      {/* Quantity Controls */}
      <div className="w-32 mx-4 mt-2 md:mt-0">
        <div className="flex items-center border rounded overflow-hidden">
          <button 
            className="px-3 py-1 text-lg bg-gray-100 hover:bg-gray-200 transition disabled:opacity-50"
            onClick={() => handleQuantityChange(-1)}
            disabled={localQuantity <= 1 || isUpdating}
            aria-label="Decrease quantity"
          >
            -
          </button>
          <span className={`px-4 py-1 border-l border-r flex-grow text-center ${isUpdating ? 'text-gray-400' : ''}`}>
            {localQuantity}
          </span>
          <button 
            className="px-3 py-1 text-lg bg-gray-100 hover:bg-gray-200 transition disabled:opacity-50"
            onClick={() => handleQuantityChange(1)}
            disabled={isUpdating}
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>
      </div>
      
      {/* Subtotal */}
      <div className="w-24 text-right font-medium mt-2 md:mt-0">
        KES{subtotal.toFixed(2)}
      </div>
    </div>
  );
});

CartItem.displayName = 'CartItem';

export default CartItem;
