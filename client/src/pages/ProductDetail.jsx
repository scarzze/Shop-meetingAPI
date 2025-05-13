import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { FaHeart, FaRegHeart, FaShoppingCart, FaStar, FaStarHalfAlt, FaRegStar, FaCheck, FaMinus } from 'react-icons/fa';
import { BiArrowBack } from 'react-icons/bi';
import { Cloudinary } from '@cloudinary/url-gen';
import { fill } from '@cloudinary/url-gen/actions/resize';
import { AuthContext } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { WishlistContext } from '../context/WishlistContext';
import { addToRecentlyViewed, getRecentlyViewed } from '../utils/localStorageService';
import API_URL from '../utils/apiConfig';

const cld = new Cloudinary({
  cloud: {
    cloudName: 'dyzqn2sju', 
  },
});

const getCloudinaryImageUrl = (publicId, width, height) => {
  // Check if the publicId is already a full URL
  if (publicId && publicId.startsWith('http')) {
    return publicId;
  }
  
  // Otherwise, generate a new URL using Cloudinary
  const image = cld.image(publicId);
  image.resize(fill().width(width).height(height));
  return image.toURL();
};

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useContext(AuthContext);
  const { addToCart, isInCart } = useContext(CartContext);
  const { addToWishlist, removeFromWishlist, isInWishlist } = useContext(WishlistContext);
  const [product, setProduct] = useState(null);
  const [selectedQuantity, setSelectedQuantity] = useState(1);
  const [inCart, setInCart] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [reviews, setReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);

  // Use a ref to track if the component is mounted
  const isMounted = React.useRef(true);
  
  // Cache for related products to avoid redundant API calls
  const [relatedProductsCache, setRelatedProductsCache] = useState({
    data: null,
    timestamp: null,
    expiryTime: 5 * 60 * 1000 // 5 minutes cache validity
  });

  useEffect(() => {
    // Set isMounted to true when the component mounts
    isMounted.current = true;
    
    // Clean up function to set isMounted to false when the component unmounts
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!isMounted.current) return;
      
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/products/${id}`);
        
        if (!response.ok) {
          throw new Error('Product not found');
        }
        
        const responseData = await response.json();
        let productData;
        
        if (!isMounted.current) return;
        
        // Handle different API response formats
        if (responseData.product) {
          productData = responseData.product;
        } else {
          productData = responseData;
        }
        
        // Debug the product data
        console.log('Product data:', productData);
        
        // Ensure product has an images array
        const imageUrl = productData.image_url || (productData.images && productData.images[0]);
        const updatedImages = imageUrl ? [imageUrl] : ['/images/placeholder.png'];
        productData.images = updatedImages;
        
        // Set default rating and reviews count if not provided
        if (!productData.rating) productData.rating = 4;
        if (!productData.reviews) productData.reviews = 0;
        
        // Ensure price is a number
        if (productData.price && typeof productData.price === 'string') {
          productData.price = parseFloat(productData.price);
        }
        
        setProduct(productData);
        
        // Check if product is in cart
        if (isInCart) {
          setInCart(isInCart(productData.id));
        }
        
        // Add to recently viewed
        addToRecentlyViewed(productData);
        
        // Get recently viewed products
        const recentProducts = getRecentlyViewed();
        // Filter out the current product from recently viewed
        if (recentProducts && recentProducts.length > 0) {
          setRecentlyViewed(recentProducts.filter(item => item && item.id !== productData.id));
        }
        
        // Check if product is in wishlist
        if (isInWishlist) {
          setIsWishlisted(isInWishlist(productData.id));
        }
        
        // Fetch related products (only if needed)
        fetchRelatedProducts(productData.category);
        
        // Only fetch reviews if the product ID is valid
        if (productData.id) {
          fetchReviews(productData.id);
        }
      } catch (error) {
        if (!isMounted.current) return;
        console.error('Error fetching product details:', error);
        setError(error.message);
      } finally {
        if (isMounted.current) {
          setLoading(false);
        }
      }
    };

    const fetchRelatedProducts = async (category) => {
      if (!isMounted.current) return;
      
      // Return cached data if available and not expired
      const now = Date.now();
      if (relatedProductsCache.data && 
          relatedProductsCache.timestamp && 
          (now - relatedProductsCache.timestamp < relatedProductsCache.expiryTime)) {
        console.log('Using cached related products');
        setRelatedProducts(relatedProductsCache.data);
        return;
      }
      
      try {
        const response = await fetch(`${API_URL}/products`);
        if (!response.ok) {
          throw new Error('Failed to fetch related products');
        }
        
        const data = await response.json();
        let productsArray = [];
        
        // Handle both array and object with products property
        if (Array.isArray(data)) {
          productsArray = data;
        } else if (data && data.products && Array.isArray(data.products)) {
          productsArray = data.products;
        }
        
        if (!isMounted.current) return;
        
        // Filter products by category and exclude current product
        const related = productsArray
          .filter(p => p.id !== parseInt(id))
          .slice(0, 4); // Limit to 4 related products
        
        // Update cache
        setRelatedProductsCache({
          data: related,
          timestamp: now,
          expiryTime: 5 * 60 * 1000
        });
        
        setRelatedProducts(related);
      } catch (error) {
        if (!isMounted.current) return;
        console.error('Error fetching related products:', error);
      }
    };
    
    const fetchReviews = async (productId) => {
      if (!isMounted.current || !productId) return;
      
      try {
        setReviewsLoading(true);
        
        // Check if the product ID is valid
        if (!productId || productId === 'undefined') {
          console.warn('Invalid product ID for fetching reviews');
          setReviews([]);
          setReviewsLoading(false);
          return;
        }
        
        console.log(`Fetching reviews for product ID: ${productId}`);
        const response = await fetch(`${API_URL}/products/${productId}/reviews`);
        
        if (!response.ok) {
          if (response.status === 404) {
            // If reviews endpoint returns 404, just set empty reviews
            console.log('No reviews found for this product');
            setReviews([]);
            setReviewsLoading(false);
            return;
          }
          throw new Error(`Failed to fetch reviews: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!isMounted.current) return;
        
        // Handle different response formats
        if (Array.isArray(data)) {
          setReviews(data);
        } else if (data && data.reviews && Array.isArray(data.reviews)) {
          setReviews(data.reviews);
        } else {
          setReviews([]);
        }
        
        setReviewsLoading(false);
      } catch (error) {
        if (!isMounted.current) return;
        console.error('Error fetching reviews:', error);
        // Set empty reviews array on error
        setReviews([]);
        setReviewsLoading(false);
      }
    };

    fetchProduct();
    
    // Cleanup function
    return () => {
      // This will be called when the component unmounts or when dependencies change
      // We already set isMounted.current = false in the other useEffect
    };
  }, [id, isInCart, isInWishlist]); // Added isInCart to dependencies

  const handleQuantityChange = (change) => {
    const newQuantity = selectedQuantity + change;
    if (newQuantity >= 1 && newQuantity <= (product?.stock || 10)) {
      setSelectedQuantity(newQuantity);
    }
  };

  const handleAddToCart = async () => {
    try {
      // Use the CartContext addToCart function which handles both authenticated and unauthenticated users
      await addToCart(product.id, selectedQuantity, product);
      setInCart(true);
      // Show success notification instead of redirecting
      setNotification({ 
        message: `${product.name} (${selectedQuantity}) added to cart successfully!`, 
        type: 'success' 
      });
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
    } catch (error) {
      console.error('Error adding to cart:', error);
      setNotification({ 
        message: error.message || 'Failed to add item to cart', 
        type: 'error' 
      });
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
    }
  };

  const toggleWishlist = () => {
    try {
      // Optimistic UI update - update UI immediately
      const newWishlistState = !isWishlisted;
      setIsWishlisted(newWishlistState);
      
      // Show notification
      setNotification({
        message: newWishlistState 
          ? `${product.name} added to wishlist` 
          : `${product.name} removed from wishlist`,
        type: 'success'
      });
      
      // Clear notification after 3 seconds
      setTimeout(() => setNotification({ message: '', type: '' }), 3000);
      
      // Perform the actual API call in the background
      if (newWishlistState) {
        // Add to wishlist
        addToWishlist(product.id, product)
          .catch(error => {
            console.error('Error adding to wishlist:', error);
            // Revert UI on error
            setIsWishlisted(false);
            setNotification({
              message: 'Failed to add to wishlist',
              type: 'error'
            });
          });
      } else {
        // Remove from wishlist
        removeFromWishlist(product.id)
          .catch(error => {
            console.error('Error removing from wishlist:', error);
            // Revert UI on error
            setIsWishlisted(true);
            setNotification({
              message: 'Failed to remove from wishlist',
              type: 'error'
            });
          });
      }
    } catch (error) {
      console.error('Error updating wishlist UI:', error);
      setNotification({
        message: 'An error occurred',
        type: 'error'
      });
    }
  };

  // Generate star rating display
  const renderRatingStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(<FaStar key={i} className="text-yellow-400" />);
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(<FaStarHalfAlt key={i} className="text-yellow-400" />);
      } else {
        stars.push(<FaRegStar key={i} className="text-yellow-400" />);
      }
    }
    
    return stars;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 md:p-10 text-center">
        <h2 className="text-2xl font-bold text-red-500 mb-4">Error</h2>
        <p className="mb-4">{error}</p>
        <button 
          onClick={() => navigate('/')} 
          className="bg-black text-white px-6 py-2 rounded hover:bg-red-600"
        >
          Return to Home
        </button>
      </div>
    );
  }

  if (!product) {
    return <div>Product not found</div>;
  }

  return (
    <div className="p-4 md:p-10 relative">
      {/* Notification */}
      {notification.message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded shadow-lg ${notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {notification.message}
        </div>
      )}
      {/* Product Details */}
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="text-sm breadcrumbs mb-6">
          <ul className="flex space-x-2">
            <li><Link to="/" className="text-gray-500 hover:text-red-500 flex items-center"><BiArrowBack className="mr-1" /> Back to Home</Link></li>
            <li><span className="text-gray-500">/</span></li>
            <li><Link to="/products" className="text-gray-500 hover:text-red-500">Products</Link></li>
            <li><span className="text-gray-500">/</span></li>
            <li><span className="text-gray-900 font-medium">{product.name}</span></li>
          </ul>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Product Image */}
          <div className="md:w-1/2">
            <div className="border rounded-lg overflow-hidden bg-white shadow-md hover:shadow-lg transition-shadow p-4">
              {product && (
                <img 
                  src={product.image_url || (product.images && product.images[0]) || '/images/placeholder.png'} 
                  alt={product.name} 
                  className="w-full h-auto object-contain max-h-96"
                  onError={(e) => {
                    console.log('Image load error, using placeholder');
                    e.target.src = '/images/placeholder.png';
                    e.target.onerror = null;
                  }}
                />
              )}
            </div>
          </div>

          {/* Product Info */}
          <div className="md:w-1/2">
            {/* Category Tag */}
            <div className="mb-3">
              <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                {product.category}
              </span>
            </div>
            
            <h1 className="text-3xl font-bold mb-3">{product.name}</h1>
            
            {/* Ratings */}
            <div className="flex items-center mb-4">
              <div className="flex mr-2">
                {renderRatingStars(product.rating)}
              </div>
              <span className="text-gray-500 text-sm">{Array.isArray(product.reviews) ? product.reviews.length : (typeof product.reviews === 'number' ? product.reviews : 0)} Reviews</span>
              <span className="mx-2 text-gray-300">|</span>
              <span className={`text-sm font-medium ${product.stock > 0 ? 'text-green-500' : 'text-red-500'}`}>
                {product.stock > 0 ? (
                  <span className="flex items-center"><FaCheck className="mr-1" /> In Stock</span>
                ) : (
                  <span className="flex items-center"><FaMinus className="mr-1" /> Out of Stock</span>
                )}
              </span>
            </div>

            {/* Price */}
            <div className="mb-6">
              <span className="text-3xl font-bold text-red-500">KES {(product.price || 0).toLocaleString()}</span>
              {product.oldPrice && (
                <span className="ml-2 text-gray-500 line-through">KES {(parseInt(product.oldPrice) || 0).toLocaleString()}</span>
              )}
              {product.oldPrice && product.price && (
                <span className="ml-3 bg-red-100 text-red-600 px-2 py-1 rounded-full text-sm font-medium">
                  {Math.round(((product.oldPrice - product.price) / product.oldPrice) * 100)}% OFF
                </span>
              )}
            </div>

            {/* Description */}
            <div className="mb-6 bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Product Description</h3>
              <p className="text-gray-700 leading-relaxed">{product.description}</p>
            </div>

            {/* Quantity Selector */}
            <div className="mb-6">
              <label className="block text-gray-700 mb-2 font-medium">Quantity</label>
              <div className="flex items-center">
                <button 
                  className="px-4 py-2 border rounded-l-md bg-gray-100 hover:bg-gray-200 transition-colors"
                  onClick={() => setSelectedQuantity(Math.max(1, selectedQuantity - 1))}
                >
                  -
                </button>
                <input 
                  type="number" 
                  min="1" 
                  value={selectedQuantity} 
                  onChange={(e) => setSelectedQuantity(parseInt(e.target.value) || 1)}
                  className="w-16 text-center border-t border-b py-2"
                />
                <button 
                  className="px-4 py-2 border rounded-r-md bg-gray-100 hover:bg-gray-200 transition-colors"
                  onClick={() => setSelectedQuantity(selectedQuantity + 1)}
                >
                  +
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4 mb-6">
              <button 
                className="flex items-center justify-center bg-red-500 text-white px-8 py-3 rounded-md hover:bg-red-600 transition-colors font-medium"
                onClick={handleAddToCart}
              >
                <FaShoppingCart className="mr-2" />
                {inCart ? 'Update Cart' : 'Add to Cart'}
              </button>
              
              <button 
                className="flex items-center justify-center border border-gray-300 px-8 py-3 rounded-md hover:bg-gray-50 transition-colors"
                onClick={toggleWishlist}
              >
                {isWishlisted ? 
                  <><FaHeart className="mr-2 text-red-500" /> Remove from Wishlist</> : 
                  <><FaRegHeart className="mr-2" /> Add to Wishlist</>}
              </button>
            </div>

            {/* Product Meta */}
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1"><span className="font-medium">SKU:</span> {product.id}</p>
              <p className="text-sm text-gray-500 mb-1"><span className="font-medium">Category:</span> {product.category}</p>
              <p className="text-sm text-gray-500 mb-1"><span className="font-medium">Availability:</span> {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}</p>
            </div>
          </div>
        </div>

        {/* Recently Viewed Products */}
        {recentlyViewed.length > 0 && (
          <section className="mt-16">
            <div className="flex justify-between items-center border-b pb-4 mb-6">
              <div className="flex items-center">
                <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
                <h2 className="text-xl font-bold">Recently Viewed</h2>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
              {recentlyViewed.map((product, i) => (
                <ProductCard key={i} product={product} />
              ))}
            </div>
          </section>
        )}
        
        {/* Product Reviews */}
        <section className="mt-16">
          <div className="flex justify-between items-center border-b pb-4 mb-6">
            <div className="flex items-center">
              <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
              <h2 className="text-xl font-bold">Product Reviews ({reviews.length})</h2>
            </div>
          </div>
          {reviewsLoading ? (
            <div className="flex justify-center items-center h-24">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-500"></div>
            </div>
          ) : reviews.length > 0 ? (
            <div className="space-y-6">
              {reviews.map((review, index) => (
                <div key={index} className="border p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">{review.username}</h3>
                      <div className="text-yellow-400 text-sm">
                        {renderRatingStars(review.rating)}
                      </div>
                    </div>
                    <span className="text-gray-500 text-sm">
                      {new Date(review.date).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{review.review}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No reviews yet for this product.</p>
          )}
        </section>
        
        {/* Related Products */}
        <section className="mt-16">
          <div className="flex justify-between items-center border-b pb-4 mb-6">
            <div className="flex items-center">
              <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
              <h2 className="text-xl font-bold">You Might Also Like</h2>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {relatedProducts.map((product, i) => (
              <ProductCard key={i} product={product} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default ProductDetail;
