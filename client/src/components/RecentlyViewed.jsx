import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecentlyViewed } from '../utils/localStorageService';
import ProductCard from './ProductCard';

const RecentlyViewed = () => {
  const [recentProducts, setRecentProducts] = useState([]);

  useEffect(() => {
    // Get recently viewed products from local storage
    const products = getRecentlyViewed();
    setRecentProducts(products);

    // Listen for storage events to update when local storage changes
    const handleStorageChange = () => {
      const updatedProducts = getRecentlyViewed();
      setRecentProducts(updatedProducts);
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  if (recentProducts.length === 0) {
    return null; // Don't render anything if no recently viewed products
  }

  return (
    <div className="my-12">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
          <h2 className="text-2xl font-bold">Recently Viewed</h2>
        </div>
        <Link to="/products" className="text-red-500 hover:underline">
          View All
        </Link>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        {recentProducts.map((product) => (
          <ProductCard key={product.id} product={product} showPrice={true} showRatings={true} />
        ))}
      </div>
    </div>
  );
};

export default RecentlyViewed;
