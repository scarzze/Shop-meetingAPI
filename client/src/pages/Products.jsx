import React, { useEffect, useState } from 'react';
import { FaFilter } from 'react-icons/fa';
import ProductCard from '../components/ProductCard';
import API_URL from '../utils/apiConfig';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    category: 'all',
    priceRange: [0, 100000],
    sortBy: 'newest'
  });

  // Categories for filter
  const categories = [
    "All Categories",
    "Women's Fashion", 
    "Men's Fashion", 
    "Electronics", 
    "Home & Lifestyle", 
    "Medicine",
    "Sports & Outdoor", 
    "Baby's & Toys", 
    "Groceries & Pets", 
    "Health & Beauty"
  ];

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        
        // First check if the API is available
        const apiResponse = await fetch(`${API_URL}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
        
        if (!apiResponse.ok) {
          throw new Error(`API server is not responding correctly. Status: ${apiResponse.status}`);
        }
        
        // Now fetch the products
        const response = await fetch(`${API_URL}/products`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch products. Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process products data - Handle both array and object with products property
        let productsArray = [];
        
        if (Array.isArray(data)) {
          productsArray = data;
        } else if (data && typeof data === 'object' && 'products' in data && Array.isArray(data.products)) {
          // This is the expected format from the API: {products: Array}
          productsArray = data.products;
        } else {
          console.error('Data received is not an array:', data);
          throw new Error('Invalid data format received from API');
        }
        
        // Debug log to verify the data structure
        console.log('Products array extracted successfully:', productsArray);
        
        // Process the products array
        const processedData = productsArray.map(product => ({
          ...product,
          rating: product.rating || 4,
          reviews: product.reviews || 0,
          currentPrice: product.price,
          oldPrice: product.oldPrice,
          image: product.image_url,
        }));
        setProducts(processedData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching products:', error);
        setError(`Failed to load products: ${error.message}. API URL: ${API_URL}`);
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Filter products based on selected filters
  const filteredProducts = products.filter(product => {
    // Filter by category
    if (filters.category !== 'all' && product.category !== filters.category) {
      return false;
    }
    
    // Filter by price range
    if (product.price < filters.priceRange[0] || product.price > filters.priceRange[1]) {
      return false;
    }
    
    return true;
  });

  // Sort products
  const sortedProducts = [...filteredProducts].sort((a, b) => {
    switch (filters.sortBy) {
      case 'price-low':
        return a.price - b.price;
      case 'price-high':
        return b.price - a.price;
      case 'rating':
        return b.rating - a.rating;
      case 'newest':
      default:
        return new Date(b.created_at || Date.now()) - new Date(a.created_at || Date.now());
    }
  });

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

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
        <h1 className="text-3xl font-bold mb-2">All Products</h1>
        <div className="flex items-center text-gray-500">
          <span>Home</span>
          <span className="mx-2">/</span>
          <span className="text-black">Products</span>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Filters Sidebar */}
        <div className="w-full md:w-1/4 bg-white p-4 rounded-lg shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Filters</h2>
            <FaFilter className="text-gray-500" />
          </div>

          {/* Categories Filter */}
          <div className="mb-6">
            <h3 className="font-medium mb-3">Categories</h3>
            <select 
              className="w-full p-2 border rounded-md"
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              {categories.map((category, index) => (
                <option key={index} value={index === 0 ? 'all' : category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Price Range Filter */}
          <div className="mb-6">
            <h3 className="font-medium mb-3">Price Range</h3>
            <div className="flex items-center justify-between">
              <span>KES {filters.priceRange[0]}</span>
              <span>KES {filters.priceRange[1]}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="10000" 
              step="100"
              className="w-full mt-2 accent-red-500"
              value={filters.priceRange[1]}
              onChange={(e) => handleFilterChange('priceRange', [filters.priceRange[0], parseInt(e.target.value)])}
            />
          </div>

          {/* Sort By Filter */}
          <div className="mb-6">
            <h3 className="font-medium mb-3">Sort By</h3>
            <select 
              className="w-full p-2 border rounded-md"
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            >
              <option value="newest">Newest Arrivals</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Customer Rating</option>
            </select>
          </div>
        </div>

        {/* Products Grid */}
        <div className="w-full md:w-3/4">
          <div className="flex justify-between items-center mb-4">
            <p className="text-gray-600">Showing {sortedProducts.length} products</p>
            <div className="flex items-center">
              <span className="mr-2 text-gray-600">View:</span>
              <button className="p-1 border rounded mr-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button className="p-1 border rounded bg-gray-100">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>

          {sortedProducts.length === 0 ? (
            <div className="flex justify-center items-center h-64 bg-gray-50 rounded-lg">
              <p className="text-gray-500 text-lg">No products found matching your criteria</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortedProducts.map((product) => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  showPrice={true} 
                  showRatings={true} 
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          <div className="flex justify-center mt-8">
            <div className="flex space-x-1">
              <button className="px-3 py-1 border rounded hover:bg-gray-100">&lt;</button>
              <button className="px-3 py-1 border rounded bg-red-500 text-white">1</button>
              <button className="px-3 py-1 border rounded hover:bg-gray-100">2</button>
              <button className="px-3 py-1 border rounded hover:bg-gray-100">3</button>
              <button className="px-3 py-1 border rounded hover:bg-gray-100">...</button>
              <button className="px-3 py-1 border rounded hover:bg-gray-100">10</button>
              <button className="px-3 py-1 border rounded hover:bg-gray-100">&gt;</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Products;