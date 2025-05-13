import React, { useState, useEffect } from 'react';
import api from '../utils/axiosConfig';

const PaymentOptions = () => {
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [newPaymentMethod, setNewPaymentMethod] = useState({
    card_type: 'Visa',
    last_four: '',
    cardholder_name: '',
    expiry_date: '',
    is_default: false
  });
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const fetchPaymentMethods = async () => {
    try {
      setLoading(true);
      const response = await api.get('/payment-options');
      setPaymentMethods(response.data.payment_methods || []);
    } catch (error) {
      console.error('Error fetching payment methods:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to load payment methods', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewPaymentMethod(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleAddPaymentMethod = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!newPaymentMethod.last_four || !newPaymentMethod.cardholder_name || !newPaymentMethod.expiry_date) {
      setNotification({ message: 'Please fill in all required fields', type: 'error' });
      return;
    }
    
    // Validate last four digits
    if (!/^\d{4}$/.test(newPaymentMethod.last_four)) {
      setNotification({ message: 'Last four digits must be exactly 4 numbers', type: 'error' });
      return;
    }
    
    // Validate expiry date format (MM/YY)
    if (!/^\d{2}\/\d{2}$/.test(newPaymentMethod.expiry_date)) {
      setNotification({ message: 'Expiry date must be in MM/YY format', type: 'error' });
      return;
    }
    
    try {
      setAdding(true);
      await api.post('/payment-options', newPaymentMethod);
      setNotification({ message: 'Payment method added successfully', type: 'success' });
      
      // Reset form and hide it
      setNewPaymentMethod({
        card_type: 'Visa',
        last_four: '',
        cardholder_name: '',
        expiry_date: '',
        is_default: false
      });
      setShowAddForm(false);
      
      // Refresh payment methods list
      fetchPaymentMethods();
    } catch (error) {
      console.error('Error adding payment method:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to add payment method', 
        type: 'error' 
      });
    } finally {
      setAdding(false);
    }
  };

  const handleDeletePaymentMethod = async (paymentId) => {
    if (!window.confirm('Are you sure you want to delete this payment method?')) {
      return;
    }
    
    try {
      setLoading(true);
      await api.delete(`/payment-options/${paymentId}`);
      setNotification({ message: 'Payment method deleted successfully', type: 'success' });
      
      // Refresh payment methods list
      fetchPaymentMethods();
    } catch (error) {
      console.error('Error deleting payment method:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to delete payment method', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const getCardIcon = (cardType) => {
    switch (cardType?.toLowerCase()) {
      case 'visa':
        return '💳 Visa';
      case 'mastercard':
        return '💳 Mastercard';
      default:
        return '💳 Card';
    }
  };

  if (loading && paymentMethods.length === 0) {
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

      {/* Payment Methods List */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Saved Payment Methods</h3>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm"
          >
            {showAddForm ? 'Cancel' : 'Add New Payment Method'}
          </button>
        </div>

        {paymentMethods.length === 0 ? (
          <div className="bg-gray-100 p-4 rounded text-center text-gray-600">
            No payment methods saved yet.
          </div>
        ) : (
          <div className="space-y-4">
            {paymentMethods.map((method) => (
              <div key={method.id} className="border rounded p-4 flex justify-between items-center">
                <div>
                  <div className="font-medium">{getCardIcon(method.card_type)}</div>
                  <div className="text-sm text-gray-600">
                    {method.cardholder_name} • •••• {method.last_four}
                  </div>
                  <div className="text-xs text-gray-500">
                    Expires: {method.expiry_date}
                    {method.is_default && (
                      <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded">
                        Default
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDeletePaymentMethod(method.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add New Payment Method Form */}
      {showAddForm && (
        <div className="border rounded p-4 bg-gray-50 mt-6">
          <h3 className="text-lg font-medium mb-4">Add New Payment Method</h3>
          <form onSubmit={handleAddPaymentMethod} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="card_type" className="block text-sm font-medium text-gray-700 mb-1">Card Type</label>
                <select
                  id="card_type"
                  name="card_type"
                  value={newPaymentMethod.card_type}
                  onChange={handleChange}
                  className="w-full border border-gray-300 p-2 rounded"
                >
                  <option value="Visa">Visa</option>
                  <option value="Mastercard">Mastercard</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="last_four" className="block text-sm font-medium text-gray-700 mb-1">
                  Last 4 Digits <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="last_four"
                  name="last_four"
                  value={newPaymentMethod.last_four}
                  onChange={handleChange}
                  maxLength="4"
                  placeholder="1234"
                  className="w-full border border-gray-300 p-2 rounded"
                  required
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="cardholder_name" className="block text-sm font-medium text-gray-700 mb-1">
                Cardholder Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="cardholder_name"
                name="cardholder_name"
                value={newPaymentMethod.cardholder_name}
                onChange={handleChange}
                placeholder="John Doe"
                className="w-full border border-gray-300 p-2 rounded"
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="expiry_date" className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date (MM/YY) <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="expiry_date"
                  name="expiry_date"
                  value={newPaymentMethod.expiry_date}
                  onChange={handleChange}
                  placeholder="05/25"
                  maxLength="5"
                  className="w-full border border-gray-300 p-2 rounded"
                  required
                />
              </div>
              
              <div className="flex items-center h-full pt-6">
                <input
                  type="checkbox"
                  id="is_default"
                  name="is_default"
                  checked={newPaymentMethod.is_default}
                  onChange={handleChange}
                  className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                />
                <label htmlFor="is_default" className="ml-2 block text-sm text-gray-700">
                  Set as default payment method
                </label>
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={adding}
                className={`${adding ? 'bg-gray-400' : 'bg-red-500 hover:bg-red-600'} text-white px-6 py-2 rounded flex items-center justify-center`}
              >
                {adding ? (
                  <>
                    <span className="animate-spin h-4 w-4 mr-2 border-t-2 border-b-2 border-white rounded-full"></span>
                    Adding...
                  </>
                ) : 'Add Payment Method'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default PaymentOptions;
