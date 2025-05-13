import React from 'react';

const OrderSummary = ({ products }) => {
  const subtotal = products?.reduce((sum, product) => sum + product.price, 0) || 0;
  const shipping = 0; // Free shipping 

  return (
    <div className="bg-gray-50 p-6 rounded-lg">
      {products?.map((product) => (
        <div key={product.id} className="flex items-center gap-4 mb-4">
          <img src={product.image} alt={product.name} className="w-16 h-16 object-cover rounded" />
          <div className="flex-grow">
            <h4 className="font-medium">{product.name}</h4>
            <p className="text-gray-500 text-sm">Quantity: {product.quantity}</p>
          </div>
          <span className="font-medium">KES{product.price}</span>
        </div>
      ))}
      
      <div className="border-t mt-6 pt-4 space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">Subtotal:</span>
          <span className="font-medium">KES{subtotal}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Shipping:</span>
          <span className="font-medium">Free</span>
        </div>
        <div className="flex justify-between font-medium text-lg pt-2 border-t">
          <span>Total:</span>
          <span>KES{subtotal}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderSummary;