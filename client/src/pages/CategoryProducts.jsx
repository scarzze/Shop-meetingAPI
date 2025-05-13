import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import ProductCard from '../components/ProductCard';
import API_URL from '../utils/apiConfig';

const CategoryProducts = () => {
  const { category } = useParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const decodedCategory = decodeURIComponent(category);

  useEffect(() => {
    const fetchProductsByCategory = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/categories/${category}`);
        
        if (!response.ok) {
          throw new Error(`Error fetching products: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Check if data has a products property (API returns {category, products})
        const productsArray = data.products || data;
        
        if (!Array.isArray(productsArray)) {
          console.error('Unexpected data format:', data);
          throw new Error('Unexpected data format from API');
        }
        
        // Add default values for missing properties
        const processedData = productsArray.map(product => ({
          ...product,
          rating: product.rating || 4,
          reviews: product.reviews || 0,
          currentPrice: product.price,
          oldPrice: product.oldPrice || (Math.random() > 0.5 ? (product.price * 1.2).toFixed(2) : null)
        }));
        
        setProducts(processedData);
      } catch (err) {
        console.error('Error fetching products by category:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProductsByCategory();
  }, [category]);

  // Function to update product images for consistency
  const updateProductImages = (products) => {
    return products.map((product) => ({
      ...product,
      image: product.image_url,
    }));
  };

  return (
    <div className="px-4 md:px-12 lg:px-24 py-8">
      <div className="flex items-center mb-6">
        <Link to="/" className="flex items-center text-gray-600 hover:text-red-500 mr-4">
          <FaArrowLeft className="mr-2" /> Back to Home
        </Link>
        <h1 className="text-2xl font-bold">{decodedCategory}</h1>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-8">
          <p>Error: {error}</p>
          <p>Please try again later</p>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-lg text-gray-600">No products found in this category.</p>
          <Link to="/" className="inline-block mt-4 bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600">
            Return to Home
          </Link>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-gray-600">{products.length} products found</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {updateProductImages(products).map((product) => (
              <ProductCard key={product.id} product={product} showPrice={true} showRatings={true} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default CategoryProducts;
