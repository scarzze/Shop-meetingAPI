import React, { useState, useEffect } from 'react';
import api from '../utils/axiosConfig';

const MyReturns = () => {
  const [returns, setReturns] = useState([]);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);
  const [expandedReturn, setExpandedReturn] = useState(null);

  useEffect(() => {
    fetchReturns();
  }, []);

  const fetchReturns = async () => {
    try {
      setLoading(true);
      const response = await api.get('/my-returns');
      setReturns(response.data.returns || []);
    } catch (error) {
      console.error('Error fetching returns:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to load returns', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleReturnDetails = (returnId) => {
    if (expandedReturn === returnId) {
      setExpandedReturn(null);
    } else {
      setExpandedReturn(returnId);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'return requested':
        return 'bg-yellow-100 text-yellow-800';
      case 'return approved':
        return 'bg-blue-100 text-blue-800';
      case 'return processing':
        return 'bg-purple-100 text-purple-800';
      case 'returned':
        return 'bg-green-100 text-green-800';
      case 'return denied':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const calculateOrderTotal = (items) => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  if (loading && returns.length === 0) {
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
        <h3 className="text-lg font-medium mb-4">Your Returns</h3>

        {returns.length === 0 ? (
          <div className="bg-gray-100 p-6 rounded text-center text-gray-600">
            <p>You don't have any returns.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {returns.map((returnOrder) => (
              <div key={returnOrder.id} className="border rounded overflow-hidden">
                {/* Return Header */}
                <div 
                  className="bg-gray-50 p-4 flex flex-col md:flex-row justify-between items-start md:items-center cursor-pointer"
                  onClick={() => toggleReturnDetails(returnOrder.id)}
                >
                  <div>
                    <div className="flex items-center">
                      <span className="font-medium">Return for Order #{returnOrder.id}</span>
                      <span className={`ml-3 text-xs px-2 py-1 rounded-full ${getStatusColor(returnOrder.status)}`}>
                        {returnOrder.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Requested on {formatDate(returnOrder.created_at)}
                    </div>
                  </div>
                  
                  <div className="mt-2 md:mt-0 flex items-center">
                    <span className="font-medium mr-3">
                      ${calculateOrderTotal(returnOrder.items)}
                    </span>
                    <svg 
                      className={`h-5 w-5 text-gray-500 transform transition-transform ${expandedReturn === returnOrder.id ? 'rotate-180' : ''}`} 
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {/* Return Details */}
                {expandedReturn === returnOrder.id && (
                  <div className="p-4 border-t">
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Items Being Returned</h4>
                      <div className="space-y-2">
                        {returnOrder.items.map((item) => (
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
                              ${(item.quantity * item.price).toFixed(2)}
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
                          // Handle track return functionality
                          alert('Track return functionality will be implemented soon.');
                        }}
                      >
                        Track Return
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

export default MyReturns;
