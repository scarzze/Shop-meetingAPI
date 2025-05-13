import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { CartContext } from '../context/CartContext';
import { AuthContext } from '../context/AuthContext';
import CartItem from '../components/CartItem';
import { FiShoppingBag, FiArrowLeft } from 'react-icons/fi';

const Cart = () => {
  const { 
    cartItems, 
    cartTotal, 
    loading, 
    error,
    updateCartItemQuantity, 
    removeFromCart,
    fetchCartItems 
  } = useContext(CartContext);
  
  const { isAuthenticated } = useContext(AuthContext);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const navigate = useNavigate();

  const shipping = 0; // Free shipping
  const total = cartTotal + shipping;

  const handleCheckout = () => {
    if (!isAuthenticated()) {
      navigate('/login', { state: { from: '/cart' } });
      return;
    }
    navigate('/checkout');
  };

  if (loading) {
    return (
      <div className="p-4 md:p-10 flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 md:p-10 text-center">
        <h2 className="text-xl font-bold text-red-500 mb-4">Error loading cart</h2>
        <p className="mb-4">{error}</p>
        <Link to="/" className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800">
          Return to Home
        </Link>
      </div>
    );
  }
  
  // Handle cart item removal with error handling
  const handleRemoveItem = async (itemId) => {
    try {
      // We don't need to call fetchCartItems after removeFromCart
      // because removeFromCart already updates the cart state
      await removeFromCart(itemId);
      setNotification({ message: 'Item removed successfully', type: 'success' });
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
    } catch (error) {
      console.error('Error removing item:', error);
      if (error.message && error.message.includes('Authentication required')) {
        setNotification({ message: 'Please log in to manage your cart', type: 'error' });
        setTimeout(() => navigate('/login', { state: { from: '/cart' } }), 2000);
      } else {
        setNotification({ message: error.message || 'Failed to remove item', type: 'error' });
        setTimeout(() => setNotification({ message: '', type: '' }), 3000);
      }
    }
  }

  return (
    <div className="p-4 md:p-10 relative">  
      {/* Notification */}
      {notification.message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded shadow-lg ${notification.type === 'success' ? 'bg-green-100 text-green-800' : 
        notification.type === 'info' ? 'bg-blue-100 text-blue-800' : 
        notification.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
        'bg-red-100 text-red-800'}`}>
          {notification.message}
        </div>
      )}
      {/* Breadcrumb */}
      <div className="text-sm text-gray-500 mb-6">
        <Link to="/" className="hover:text-black">Home</Link> / <span className="text-black font-medium">Cart</span>
      </div>

      {cartItems.length === 0 ? (
        <div className="text-center py-16">
          <FiShoppingBag className="mx-auto text-6xl text-gray-300 mb-4" />
          <h2 className="text-2xl font-bold mb-4">Your cart is empty</h2>
          <p className="text-gray-500 mb-6">Looks like you haven't added anything to your cart yet.</p>
          <Link to="/" className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800 inline-flex items-center">
            <FiArrowLeft className="mr-2" /> Continue Shopping
          </Link>
        </div>
      ) : (
        <div>
          <h1 className="text-2xl font-bold mb-6">Shopping Cart ({cartItems.length} items)</h1>
          
          {/* Cart Header */}
          <div className="hidden md:flex border-b pb-2 font-medium text-gray-600">
            <div className="w-6"></div>
            <div className="w-20"></div>
            <div className="flex-grow mx-4">Product</div>
            <div className="w-24 text-right">Price</div>
            <div className="w-32 mx-4 text-center">Quantity</div>
            <div className="w-24 text-right">Subtotal</div>
          </div>

          {/* Cart Items */}
          <div className="divide-y">
            {cartItems.map(item => (
              <CartItem 
                key={item.item_id} 
                item={item}
                onQuantityChange={updateCartItemQuantity}
                onRemove={handleRemoveItem}
              />
            ))}
          </div>

          {/* Cart Actions */}
          <div className="flex flex-col md:flex-row justify-between items-start mt-8">
            <div className="w-full md:w-1/2 mb-6 md:mb-0">
              <div className="flex space-x-4">
                <Link to="/" className="border border-black px-4 py-2 rounded hover:bg-gray-100 inline-flex items-center">
                  <FiArrowLeft className="mr-2" /> Continue Shopping
                </Link>
              </div>
            </div>

            {/* Cart Totals */}
            <div className="w-full md:w-96">
              <h2 className="text-xl font-bold mb-4">Cart Total</h2>
              <div className="border rounded p-4">
                <div className="flex justify-between py-3 border-b">
                  <span>Subtotal:</span>
                  <span className="font-medium">KES{cartTotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between py-3 border-b">
                  <span>Shipping:</span>
                  <span className="font-medium">{shipping === 0 ? 'Free' : `KES${shipping.toFixed(2)}`}</span>
                </div>
                <div className="flex justify-between py-3">
                  <span>Total:</span>
                  <span className="font-bold">KES{total.toFixed(2)}</span>
                </div>
                <button 
                  className="w-full bg-red-500 text-white mt-4 py-3 rounded hover:bg-red-600 transition"
                  onClick={handleCheckout}
                >
                  Proceed to Checkout
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;