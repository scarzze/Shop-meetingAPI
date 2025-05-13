import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import API_URL from '../utils/apiConfig';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      if (!query) {
        setProducts([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/products`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch products');
        }
        
        const data = await response.json();
        
        // Filter products based on search query (case insensitive)
        const lowerCaseQuery = query.toLowerCase();
        const filteredProducts = data.filter(product => 
          product.name.toLowerCase().includes(lowerCaseQuery) || 
          product.category.toLowerCase().includes(lowerCaseQuery)
        );
        
        // Process products data
        const processedData = filteredProducts.map(product => ({
          ...product,
          rating: product.rating || 4,
          reviews: product.reviews || 0,
          currentPrice: product.price,
          // Add image property that points to image_url for backward compatibility
          image: product.image_url,
        }));
        
        setProducts(processedData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching products:', error);
        setError('Failed to load products. Please try again later.');
        setLoading(false);
      }
    };

    fetchProducts();
  }, [query]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="px-4 md:px-12 lg:px-24 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Search Results</h1>
        <div className="flex items-center text-gray-500">
          <span>Home</span>
          <span className="mx-2">/</span>
          <span className="text-black">Search: "{query}"</span>
        </div>
      </div>

      {/* Results count */}
      <p className="text-gray-600 mb-6">Found {products.length} results for "{query}"</p>

      {/* Products Grid */}
      {products.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600">No products found matching "{query}"</p>
          <p className="mt-2 text-gray-500">Try a different search term or browse our categories</p>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
