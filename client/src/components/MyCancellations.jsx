import React, { useState, useEffect } from 'react';
import api from '../utils/axiosConfig';

const MyCancellations = () => {
  const [cancellations, setCancellations] = useState([]);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);
  const [expandedCancellation, setExpandedCancellation] = useState(null);

  useEffect(() => {
    fetchCancellations();
  }, []);

  const fetchCancellations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/my-cancellations');
      setCancellations(response.data.cancellations || []);
    } catch (error) {
      console.error('Error fetching cancellations:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to load cancellations', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleCancellationDetails = (cancellationId) => {
    if (expandedCancellation === cancellationId) {
      setExpandedCancellation(null);
    } else {
      setExpandedCancellation(cancellationId);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const calculateOrderTotal = (items) => {
    return items.reduce((total, item) => total + (parseFloat(item.price) * item.quantity), 0).toFixed(2);
  };

  if (loading && cancellations.length === 0) {
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
        <h3 className="text-lg font-medium mb-4">Your Cancelled Orders</h3>

        {cancellations.length === 0 ? (
          <div className="bg-gray-100 p-6 rounded text-center text-gray-600">
            <p>You don't have any cancelled orders.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {cancellations.map((cancellation) => (
              <div key={cancellation.id} className="border rounded overflow-hidden">
                {/* Cancellation Header */}
                <div 
                  className="bg-gray-50 p-4 flex flex-col md:flex-row justify-between items-start md:items-center cursor-pointer"
                  onClick={() => toggleCancellationDetails(cancellation.id)}
                >
                  <div>
                    <div className="flex items-center">
                      <span className="font-medium">Cancelled Order #{cancellation.id}</span>
                      <span className="ml-3 text-xs px-2 py-1 rounded-full bg-red-100 text-red-800">
                        Cancelled
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Cancelled on {formatDate(cancellation.created_at)}
                    </div>
                  </div>
                  
                  <div className="mt-2 md:mt-0 flex items-center">
                    <span className="font-medium mr-3">
                      ${calculateOrderTotal(cancellation.items)}
                    </span>
                    <svg 
                      className={`h-5 w-5 text-gray-500 transform transition-transform ${expandedCancellation === cancellation.id ? 'rotate-180' : ''}`} 
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {/* Cancellation Details */}
                {expandedCancellation === cancellation.id && (
                  <div className="p-4 border-t">
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Cancelled Items</h4>
                      <div className="space-y-2">
                        {cancellation.items.map((item) => (
                          <div key={item.id} className="flex justify-between items-center py-2 border-b">
                            <div className="flex items-center">
                              <div className="ml-3">
                                <div>{item.product_name}</div>
                                <div className="text-sm text-gray-600">
                                  Qty: {item.quantity} × ${parseFloat(item.price).toFixed(2)}
                                </div>
                              </div>
                            </div>
                            <div className="font-medium">
                              ${(item.quantity * parseFloat(item.price)).toFixed(2)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mt-4 flex justify-end">
                      <button
                        className="text-red-500 hover:text-red-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Handle reorder functionality
                          alert('Reorder functionality will be implemented soon.');
                        }}
                      >
                        Reorder
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyCancellations;
