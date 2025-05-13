import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import OrderSummary from '../components/OrderSummary';
import { CartContext } from '../context/CartContext';
import { AuthContext } from '../context/AuthContext';
import { isValidEmail, isValidPhone, isValidName, isValidAddress } from '../utils/validation';

const Checkout = () => {
  const { cartItems, cartTotal, loading, error, fetchCartItems, clearCart } = useContext(CartContext);
  const { isAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();
  const [notification, setNotification] = useState({ message: '', type: '' });
  
  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      navigate('/login', { state: { from: '/checkout' } });
      return;
    }
    
    // Fetch latest cart items
    fetchCartItems();
  }, [isAuthenticated, navigate, fetchCartItems]);

  const [formData, setFormData] = useState({
    firstName: '',
    companyName: '',
    streetAddress: '',
    apartment: '',
    city: '',
    phone: '',
    email: '',
    saveInfo: true,
  });

  const [coupon, setCoupon] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');

  const [formErrors, setFormErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
    
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  const validateForm = () => {
    const errors = {};
    
    // Validate first name
    if (!isValidName(formData.firstName)) {
      errors.firstName = 'First name is required';
    }
    
    // Validate street address
    if (!isValidAddress(formData.streetAddress)) {
      errors.streetAddress = 'Please enter a valid street address';
    }
    
    // Validate city
    if (!isValidName(formData.city)) {
      errors.city = 'City is required';
    }
    
    // Validate phone
    if (!isValidPhone(formData.phone)) {
      errors.phone = 'Please enter a valid phone number';
    }
    
    // Validate email
    if (!isValidEmail(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCouponApply = () => {
    setNotification({ message: `Coupon "${coupon}" applied!`, type: 'success' });
    setTimeout(() => setNotification({ message: '', type: '' }), 3000);
  };

  const handleOrder = (e) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      setNotification({ message: 'Please correct the errors in the form', type: 'error' });
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
      return;
    }
    
    try {
      // Here you would typically make an API call to place the order
      // For now, we'll just simulate a successful order
      setNotification({ message: 'Order placed successfully!', type: 'success' });
      
      // Clear the cart after successful order
      clearCart();
      
      // Redirect to home page after a delay
      setTimeout(() => {
        navigate('/');
      }, 3000);
    } catch (error) {
      console.error('Error placing order:', error);
      setNotification({ message: error.message || 'Failed to place order', type: 'error' });
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
    }
  };

  const shipping = 0; // Free shipping
  const total = cartTotal + shipping;
  
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
        <h2 className="text-xl font-bold text-red-500 mb-4">Error loading checkout</h2>
        <p className="mb-4">{error}</p>
        <button 
          onClick={() => navigate('/')}
          className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
        >
          Return to Home
        </button>
      </div>
    );
  }
  
  if (cartItems.length === 0) {
    return (
      <div className="p-4 md:p-10 text-center">
        <h2 className="text-xl font-bold mb-4">Your cart is empty</h2>
        <p className="mb-4">Add some items to your cart before proceeding to checkout.</p>
        <button 
          onClick={() => navigate('/cart')}
          className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
        >
          Return to Cart
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-2 gap-12 relative">
      {/* Notification */}
      {notification.message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded shadow-lg ${notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {notification.message}
        </div>
      )}
      {/* Billing Details */}
      <div>
        <h2 className="text-2xl font-semibold mb-6">Billing Details</h2>
        <form onSubmit={handleOrder} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">First Name*</label>
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
              className={`w-full border ${formErrors.firstName ? 'border-red-500' : 'border-gray-300'} px-4 py-2 rounded-md`}
            />
            {formErrors.firstName && (
              <p className="text-red-500 text-xs mt-1">{formErrors.firstName}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Last Name</label>
            <input
              type="text"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              className="w-full border border-gray-300 px-4 py-2 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Street Address*</label>
            <input
              type="text"
              name="streetAddress"
              value={formData.streetAddress}
              onChange={handleChange}
              required
              className={`w-full border ${formErrors.streetAddress ? 'border-red-500' : 'border-gray-300'} px-4 py-2 rounded-md`}
            />
            {formErrors.streetAddress && (
              <p className="text-red-500 text-xs mt-1">{formErrors.streetAddress}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Apartment, floor, etc. (optional)</label>
            <input
              type="text"
              name="apartment"
              value={formData.apartment}
              onChange={handleChange}
              className="w-full border border-gray-300 px-4 py-2 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Town/City*</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              required
              className={`w-full border ${formErrors.city ? 'border-red-500' : 'border-gray-300'} px-4 py-2 rounded-md`}
            />
            {formErrors.city && (
              <p className="text-red-500 text-xs mt-1">{formErrors.city}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Phone Number*</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              className={`w-full border ${formErrors.phone ? 'border-red-500' : 'border-gray-300'} px-4 py-2 rounded-md`}
            />
            {formErrors.phone && (
              <p className="text-red-500 text-xs mt-1">{formErrors.phone}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email Address*</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className={`w-full border ${formErrors.email ? 'border-red-500' : 'border-gray-300'} px-4 py-2 rounded-md`}
            />
            {formErrors.email && (
              <p className="text-red-500 text-xs mt-1">{formErrors.email}</p>
            )}
          </div>
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              name="saveInfo"
              checked={formData.saveInfo}
              onChange={handleChange}
              className="w-4 h-4 text-red-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Save this information for faster check-out next time
            </span>
          </label>
        </form>
      </div>

      {/* Order Summary */}
      <div>
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold mb-6">Order Summary</h2>
          <OrderSummary products={cartItems.map(item => ({
            id: item.item_id,
            name: item.name,
            price: parseFloat(item.price) * parseInt(item.quantity, 10),
            image: item.image_url,
            quantity: item.quantity
          }))} />

          {/* Payment Method */}
          <div className="mt-4 space-y-2 bg-gray-100 p-6 rounded-lg">
            <label className="flex items-center">
              <input
                type="radio"
                name="payment"
                value="bank"
                checked={paymentMethod === 'bank'}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="mr-2"
              />
              Bank
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="payment"
                value="cash"
                checked={paymentMethod === 'cash'}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="mr-2"
              />
              Cash on delivery
            </label>

            {/* Coupon Code */}
            <div className="flex items-center mt-4 space-x-2">
              <input
                type="text"
                placeholder="Coupon Code"
                value={coupon}
                onChange={(e) => setCoupon(e.target.value)}
                className="flex-grow border border-gray-300 px-4 py-2 rounded-md"
              />
              <button
                type="button"
                onClick={handleCouponApply}
                className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
              >
                Apply Coupon
              </button>
            </div>

            <button
              type="submit"
              onClick={handleOrder}
              className="w-full bg-red-500 text-white py-3 rounded-md mt-6 hover:bg-red-600"
              disabled={cartItems.length === 0}
            >
              Place Order {cartItems.length > 0 && `(KES${total.toFixed(2)})`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
