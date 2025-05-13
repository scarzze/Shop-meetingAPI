import React, { useState, useEffect } from 'react';
import api from '../utils/axiosConfig';

const AddressBook = () => {
  const [addressData, setAddressData] = useState({
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: ''
  });
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchAddress = async () => {
      try {
        setLoading(true);
        const response = await api.get('/address-book');
        const { address } = response.data;
        
        setAddressData({
          address_line1: address.address_line1 || '',
          address_line2: address.address_line2 || '',
          city: address.city || '',
          state: address.state || '',
          postal_code: address.postal_code || '',
          country: address.country || ''
        });
      } catch (error) {
        console.error('Error fetching address:', error);
        setNotification({ 
          message: error.response?.data?.error || 'Failed to load address data', 
          type: 'error' 
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAddress();
  }, []);

  const handleChange = (e) => {
    setAddressData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      await api.post('/address-book', addressData);
      setNotification({ message: 'Address updated successfully', type: 'success' });
    } catch (error) {
      console.error('Error updating address:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to update address', 
        type: 'error' 
      });
    } finally {
      setSaving(false);
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

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label htmlFor="address_line1" className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
            <input
              type="text"
              id="address_line1"
              name="address_line1"
              value={addressData.address_line1}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              placeholder="Street address, P.O. box, company name"
            />
          </div>
          
          <div>
            <label htmlFor="address_line2" className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
            <input
              type="text"
              id="address_line2"
              name="address_line2"
              value={addressData.address_line2}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              placeholder="Apartment, suite, unit, building, floor, etc."
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input
                type="text"
                id="city"
                name="city"
                value={addressData.city}
                onChange={handleChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
            
            <div>
              <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">State/Province/Region</label>
              <input
                type="text"
                id="state"
                name="state"
                value={addressData.state}
                onChange={handleChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
              <input
                type="text"
                id="postal_code"
                name="postal_code"
                value={addressData.postal_code}
                onChange={handleChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
            
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <input
                type="text"
                id="country"
                name="country"
                value={addressData.country}
                onChange={handleChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4 mt-8">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="border border-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className={`${saving ? 'bg-gray-400' : 'bg-red-500 hover:bg-red-600'} text-white px-6 py-2 rounded flex items-center justify-center`}
          >
            {saving ? (
              <>
                <span className="animate-spin h-4 w-4 mr-2 border-t-2 border-b-2 border-white rounded-full"></span>
                Saving...
              </>
            ) : 'Save Address'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddressBook;
