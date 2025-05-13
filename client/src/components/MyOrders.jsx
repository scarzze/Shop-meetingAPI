import React, { useState, useEffect } from 'react';
import api from '../utils/axiosConfig';

const MyOrders = () => {
  const [orders, setOrders] = useState([]);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(true);
  const [expandedOrder, setExpandedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/my-orders');
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
      setNotification({ 
        message: error.response?.data?.error || 'Failed to load orders', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleOrderDetails = (orderId) => {
    if (expandedOrder === orderId) {
      setExpandedOrder(null);
    } else {
      setExpandedOrder(orderId);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'shipped':
        return 'bg-purple-100 text-purple-800';
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'returned':
      case 'return requested':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const calculateOrderTotal = (items) => {
    return items.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  if (loading && orders.length === 0) {
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
        <h3 className="text-lg font-medium mb-4">Your Orders</h3>

        {orders.length === 0 ? (
          <div className="bg-gray-100 p-6 rounded text-center text-gray-600">
            <p className="mb-4">You haven't placed any orders yet.</p>
            <a href="/products" className="text-red-500 hover:text-red-700 font-medium">
              Browse Products
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="border rounded overflow-hidden">
                {/* Order Header */}
                <div 
                  className="bg-gray-50 p-4 flex flex-col md:flex-row justify-between items-start md:items-center cursor-pointer"
                  onClick={() => toggleOrderDetails(order.id)}
                >
                  <div>
                    <div className="flex items-center">
                      <span className="font-medium">Order #{order.id}</span>
                      <span className={`ml-3 text-xs px-2 py-1 rounded-full ${getStatusColor(order.status)}`}>
                        {order.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Placed on {formatDate(order.created_at)}
                    </div>
                  </div>
                  
                  <div className="mt-2 md:mt-0 flex items-center">
                    <span className="font-medium mr-3">
                      ${calculateOrderTotal(order.items)}
                    </span>
                    <svg 
                      className={`h-5 w-5 text-gray-500 transform transition-transform ${expandedOrder === order.id ? 'rotate-180' : ''}`} 
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {/* Order Details */}
                {expandedOrder === order.id && (
                  <div className="p-4 border-t">
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Items</h4>
                      <div className="space-y-2">
                        {order.items.map((item) => (
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
                    
                    {order.shipping_address && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Shipping Address</h4>
                        <div className="text-sm text-gray-600">
                          {order.shipping_address}
                        </div>
                      </div>
                    )}
                    
                    {order.payment && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Payment Information</h4>
                        <div className="text-sm text-gray-600">
                          <div>Method: {order.payment.payment_method}</div>
                          <div>Status: {order.payment.status}</div>
                          <div>Amount: ${parseFloat(order.payment.amount).toFixed(2)}</div>
                        </div>
                      </div>
                    )}
                    
                    <div className="mt-4 flex justify-end">
                      <button
                        className="text-red-500 hover:text-red-700 mr-4"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Handle track order functionality
                          alert('Track order functionality will be implemented soon.');
                        }}
                      >
                        Track Order
                      </button>
                      
                      {['Pending', 'Processing'].includes(order.status) && (
                        <button
                          className="text-red-500 hover:text-red-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Handle cancel order functionality
                            alert('Cancel order functionality will be implemented soon.');
                          }}
                        >
                          Cancel Order
                        </button>
                      )}
                      
                      {['Delivered'].includes(order.status) && (
                        <button
                          className="text-red-500 hover:text-red-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Handle return order functionality
                            alert('Return order functionality will be implemented soon.');
                          }}
                        >
                          Return Order
                        </button>
                      )}
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

export default MyOrders;
