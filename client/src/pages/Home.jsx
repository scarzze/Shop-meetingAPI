import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import API_URL from '../utils/apiConfig';
import { FaGamepad } from 'react-icons/fa';
import { FiTruck, FiHeadphones, FiShield, FiPhone, FiMonitor, FiWatch, FiCamera } from 'react-icons/fi';
import { HiOutlineArrowLeft, HiOutlineArrowRight } from 'react-icons/hi';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';
import FlashSalesTimer from '../components/FlashSalesTimer';
import ProductCard from '../components/ProductCard';
import RecentlyViewed from '../components/RecentlyViewed';
import { Cloudinary } from '@cloudinary/url-gen';
import { fill } from '@cloudinary/url-gen/actions/resize';

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

const updateProductImages = (products) => {
  return products.map((product) => ({
    ...product,
    image: product.image_url,
  }));
};

const Home = () => {
  const [flashSales, setFlashSales] = useState([]);
  const [bestSelling, setBestSelling] = useState([]);
  const [exploreProducts, setExploreProducts] = useState([]);
  const [newArrivals, setNewArrivals] = useState([]);
  const navigate = useNavigate();

  // Set deadline for flash sale - 3 days from now
  const flashSaleDeadline = new Date();
  flashSaleDeadline.setDate(flashSaleDeadline.getDate() + 3);

  const categories = [
    "Women's Fashion", "Men's Fashion", "Electronics", "Home & Lifestyle", "Medicine",
    "Sports & Outdoor", "Baby's & Toys", "Groceries & Pets", "Health & Beauty"
  ];

  const featureCards = [
    { icon: <FiTruck />, title: 'FREE AND FAST DELIVERY', desc: 'Free delivery for all orders over KES140' },
    { icon: <FiHeadphones />, title: '24/7 CUSTOMER SERVICE', desc: 'Friendly 24/7 customer support' },
    { icon: <FiShield />, title: 'MONEY BACK GUARANTEE', desc: 'We return money within 30 days' },
  ];

  const categoryIcons = [
    { label: 'Phones', icon: <FiPhone className="text-3xl"/>, category: "Electronics" },
    { label: 'Computers', icon: <FiMonitor className="text-3xl"/>, category: "Electronics" },
    { label: 'SmartWatch', icon: <FiWatch className="text-3xl"/>, category: "Electronics" },
    { label: 'Camera', icon: <FiCamera className="text-3xl"/>, category: "Electronics" },
    { label: 'HeadPhones', icon: <FiHeadphones className="text-3xl"/>, category: "Electronics" },
    { label: 'Gaming', icon: <FaGamepad className="text-3xl"/>, category: "Electronics" },
  ];

  const audioPromotion = {
    title: 'Enhance Your Music Experience',
    image: '/images/JBL.png',
    deadline: flashSaleDeadline
  };

    useEffect(() => {
      const fetchProducts = async () => {
        try {
          const response = await fetch(`${API_URL}/products`); 
          if (!response.ok) {
            throw new Error('Failed to fetch products');
          }
          
          const data = await response.json();
          
          // Add debug log to see what data structure we're receiving
          console.log('API Response:', data);
          
          // Check if data is an array or if it has a products property containing an array
          const productsArray = Array.isArray(data) ? data : 
                              (data && data.products && Array.isArray(data.products) ? data.products : []);
          
          console.log('Extracted products array:', productsArray);
          
          // Add default values for missing properties
          const processedData = productsArray.map(product => ({
            ...product,
            rating: product.rating || 4,
            reviews: product.reviews || 0,
            currentPrice: product.price, // Use price from API as currentPrice
            // Generate random oldPrice for display purposes (in a real app, this would come from the API)
            oldPrice: product.oldPrice || (Math.random() > 0.5 ? (product.price * 1.2).toFixed(2) : null)
          }));

          // Update images for each category
          // If specific categories don't exist, distribute products evenly
          const flashSalesProducts = processedData.filter(product => 
            product.category === 'Flash Sales' || product.category === 'Electronics'
          ).slice(0, 4);
          
          const bestSellingProducts = processedData.filter(product => 
            product.category === 'Best Selling' || product.category === 'Men\'s Fashion'
          ).slice(0, 4);
          
          const exploreProducts = processedData.filter(product => 
            product.category === 'Explore Products' || product.category === 'Women\'s Fashion'
          ).slice(0, 8);
          
          const newArrivalsProducts = processedData.filter(product => 
            product.category === 'New Arrivals' || product.category === 'Home & Lifestyle'
          ).slice(0, 4);

          setFlashSales(updateProductImages(flashSalesProducts));
          setBestSelling(updateProductImages(bestSellingProducts));
          setExploreProducts(updateProductImages(exploreProducts));
          setNewArrivals(updateProductImages(newArrivalsProducts));
        } catch (error) {
          console.error('Error fetching products:', error);
          // Set fallback data if fetch fails
          setFlashSales([]);
          setBestSelling([]);
          setExploreProducts([]);
          setNewArrivals([]);
        }
      };

      fetchProducts();
    }, []);

  return (
    <div className="px-4 md:px-12 lg:px-24">
      {/* Hero Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <ul className="hidden md:flex flex-col text-sm font-medium text-gray-700 space-y-4">
          {categories.map(cat => (
            <li key={cat} className="hover:text-red-500 cursor-pointer flex justify-between items-center">
              <Link to={`/category/${encodeURIComponent(cat)}`} className="flex-grow">
                {cat}
              </Link>
              {cat.includes('Fashion') && <span className="text-gray-400">›</span>}
            </li>
          ))}
        </ul>
        <div className="md:col-span-3">
          <Carousel 
            autoPlay 
            infiniteLoop 
            showThumbs={false} 
            showStatus={false}
            showIndicators={true}
            className="rounded-lg overflow-hidden"
          >
            <div>
              <img src="/images/iphoneke.jpg" alt="iPhone 14 banner" className="w-full h-126 object-cover" />
              <div className="absolute inset-0 flex flex-col justify-center px-12 bg-gradient-to-r from-black/70 to-transparent">
                <div className="max-w-md">
                  <span className="bg-red-500 text-white px-4 py-1 rounded-full text-sm font-medium mb-4 inline-block">Special Offer</span>
                  <h2 className="text-5xl font-bold text-white mb-4 leading-tight">Up to <span className="text-red-500">10% off</span> Voucher</h2>
                  <p className="text-gray-200 mb-6 text-lg">Exclusive deals on our latest products. Limited time offer.</p>
                </div>
              </div>
            </div>
            <div><img src="/images/levitan.jpg" alt="banner"  className="w-full h-126 object-cover"/></div>
          </Carousel>
        </div>
      </div>

      {/* Flash Sales Section */}
      <section className="mt-16">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center">
            <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
            <h2 className="text-xl font-bold">Today's</h2>
          </div>
          <div className="flex items-center">
            <h3 className="text-xl font-bold mr-6">Flash Sales</h3>
            <FlashSalesTimer deadline={flashSaleDeadline.toString()} />
          </div>
          <div className="flex">
            <button className="p-2 border rounded-full mr-2 hover:bg-gray-100">
              <HiOutlineArrowLeft className="text-lg" />
            </button>
            <button className="p-2 border rounded-full hover:bg-gray-100">
              <HiOutlineArrowRight className="text-lg" />
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          {flashSales.map((product, i) => (
            <ProductCard key={i} product={product} showPrice={true} showRatings={true} />
          ))}
        </div>
        <div className="text-center mt-8">
          <Link 
            to="/products" 
            className="inline-block border px-8 py-2 text-sm rounded text-red-500 border-red-500 hover:bg-red-500 hover:text-white font-medium transition duration-300"
            onClick={() => window.scrollTo(0, 0)}
          >
            View All Products
          </Link>
        </div>
      </section>

      {/* Browse By Category Section */}
      <section className="mt-16">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center">
            <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
            <h2 className="text-xl font-bold">Categories</h2>
          </div>
          <h3 className="text-xl font-bold">Browse By Category</h3>
          <div className="flex">
            <button className="p-2 border rounded-full mr-2 hover:bg-gray-100">
              <HiOutlineArrowLeft className="text-lg" />
            </button>
            <button className="p-2 border rounded-full hover:bg-gray-100">
              <HiOutlineArrowRight className="text-lg" />
            </button>
          </div>
        </div>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 mt-6">
          {categoryIcons.map((cat, i) => (
            <div 
              key={i} 
              className="flex flex-col items-center justify-center border py-6 rounded-lg hover:border-red-500 cursor-pointer hover:bg-gray-50 transition-all"
              onClick={() => {
                navigate(`/category/${encodeURIComponent(cat.category)}`);
                window.scrollTo(0, 0); // Scroll to top when navigating
              }}
              role="button"
              aria-label={`Browse ${cat.label} category`}
            >
              <div className="h-12 w-12 flex items-center justify-center">
                {cat.icon}
              </div>
              <span className="text-sm mt-3">{cat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Audio Promotion Banner */}
      <section className="mt-16 bg-black text-white rounded-lg p-8">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-6 md:mb-0">
            <div className="text-green-500 font-medium mb-2">Categories</div>
            <h2 className="text-3xl font-bold mb-8">{audioPromotion.title}</h2>
            <div className="flex gap-4 mb-8">
              <div className="bg-white rounded-full h-16 w-16 flex flex-col items-center justify-center text-black">
                <span className="font-bold">23</span>
                <span className="text-xs">Days</span>
              </div>
              <div className="bg-white rounded-full h-16 w-16 flex flex-col items-center justify-center text-black">
                <span className="font-bold">05</span>
                <span className="text-xs">Hours</span>
              </div>
              <div className="bg-white rounded-full h-16 w-16 flex flex-col items-center justify-center text-black">
                <span className="font-bold">59</span>
                <span className="text-xs">Minutes</span>
              </div>
              <div className="bg-white rounded-full h-16 w-16 flex flex-col items-center justify-center text-black">
                <span className="font-bold">35</span>
                <span className="text-xs">Seconds</span>
              </div>
            </div>
            <button className="bg-green-500 text-white px-6 py-2 rounded">
              Buy Now!
            </button>
          </div>
          <div className="md:w-1/2 flex justify-center">
            <img src={audioPromotion.image} alt="JBL Speaker" className="h-64 w-200 object-contain " />
          </div>
        </div>
      </section>

      {/* Best Selling Products */}
      <section className="mt-16">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center">
            <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
            <h2 className="text-xl font-bold">This Month</h2>
          </div>
          <h3 className="text-xl font-bold">Best Selling Products</h3>
          <div className="invisible">Spacer</div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          {bestSelling.map((product, i) => (
            <ProductCard key={i} product={product} showPrice={true} showRatings={true} />
          ))}
        </div>
      </section>

      {/* Explore Our Products */}
      <section className="mt-16">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center">
            <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
            <h2 className="text-xl font-bold">Our Products</h2>
          </div>
          <h3 className="text-xl font-bold">Explore Our Products</h3>
          <div className="flex">
            <button className="p-2 border rounded-full mr-2 hover:bg-gray-100">
              <HiOutlineArrowLeft className="text-lg" />
            </button>
            <button className="p-2 border rounded-full hover:bg-gray-100">
              <HiOutlineArrowRight className="text-lg" />
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          {exploreProducts.slice(0, 8).map((product, i) => (
            <ProductCard key={i} product={product} showPrice={true} showRatings={true} />
          ))}
        </div>
        <div className="text-center mt-8">
          <Link to="/products" className="inline-block bg-red-500 text-white px-8 py-2 rounded hover:bg-red-600 transition duration-300">
            View All Products
          </Link>
        </div>
      </section>

      {/* New Arrival Section */}
      <section className="mt-16">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center">
            <div className="w-5 h-10 bg-red-500 rounded mr-3"></div>
            <h2 className="text-xl font-bold">Featured</h2>
          </div>
          <h3 className="text-xl font-bold">New Arrival</h3>
          <div className="invisible">Spacer</div>
        </div>
        <div className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* First New Arrival - Larger Card */}
            <div className="md:col-span-2 bg-gradient-to-r from-gray-900 to-black text-white rounded-lg overflow-hidden h-96 relative group shadow-lg transform transition-transform duration-300 hover:scale-[1.01]">
              <img 
                src={newArrivals.length > 0 ? newArrivals[0].image_url : 'https://placehold.co/800x600/111827/FFFFFF?text=New+Arrival'} 
                alt={newArrivals.length > 0 ? newArrivals[0].name : 'New Arrival'} 
                className="w-full h-full object-cover opacity-90 group-hover:opacity-70 transition-opacity duration-300" 
              />
              <div className="absolute inset-0 flex flex-col justify-end p-8 bg-gradient-to-t from-black/80 to-transparent">
                <span className="text-red-400 text-sm font-medium mb-2">NEW ARRIVAL</span>
                <h3 className="text-2xl font-bold mb-2">{newArrivals.length > 0 ? newArrivals[0].name : 'Premium Collection'}</h3>
                <p className="mb-4 text-sm text-gray-200">{newArrivals.length > 0 ? newArrivals[0].description : 'Discover our latest premium collection with exceptional quality and design.'}</p>
                <button className="bg-transparent border border-white text-white px-4 py-2 rounded w-32 hover:bg-white hover:text-black transition-colors duration-300">
                  Shop Now
                </button>
              </div>
            </div>
            
            {/* Second New Arrival - Vertical Card */}
            <div className="flex flex-col gap-6 h-96">
              {/* Top Card */}
              <div className="flex-1 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg overflow-hidden relative group shadow-lg transform transition-transform duration-300 hover:scale-[1.01]">
                <img 
                  src={newArrivals.length > 1 ? newArrivals[1].image_url : 'https://placehold.co/400x300/1F2937/FFFFFF?text=New+Style'} 
                  alt={newArrivals.length > 1 ? newArrivals[1].name : 'New Style'} 
                  className="w-full h-full object-cover opacity-90 group-hover:opacity-70 transition-opacity duration-300" 
                />
                <div className="absolute inset-0 flex flex-col justify-end p-4 bg-gradient-to-t from-black/80 to-transparent">
                  <span className="text-red-400 text-xs font-medium mb-1">TRENDING</span>
                  <h3 className="text-lg font-bold mb-1">{newArrivals.length > 1 ? newArrivals[1].name : 'Seasonal Collection'}</h3>
                  <button className="bg-transparent border border-white text-white px-3 py-1 rounded text-xs hover:bg-white hover:text-black transition-colors duration-300 mt-2 w-24">
                    Shop Now
                  </button>
                </div>
              </div>
              
              {/* Bottom Card - Placeholder */}
              <div className="flex-1 bg-gradient-to-r from-gray-800 to-gray-700 text-white rounded-lg overflow-hidden relative group shadow-lg transform transition-transform duration-300 hover:scale-[1.01]">
                <img 
                  src="https://placehold.co/400x300/374151/FFFFFF?text=New+Collection" 
                  alt="New Collection" 
                  className="w-full h-full object-cover opacity-90 group-hover:opacity-70 transition-opacity duration-300" 
                />
                <div className="absolute inset-0 flex flex-col justify-end p-4 bg-gradient-to-t from-black/80 to-transparent">
                  <span className="text-red-400 text-xs font-medium mb-1">EXCLUSIVE</span>
                  <h3 className="text-lg font-bold mb-1">Limited Edition</h3>
                  <button className="bg-transparent border border-white text-white px-3 py-1 rounded text-xs hover:bg-white hover:text-black transition-colors duration-300 mt-2 w-24">
                    Shop Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Recently Viewed */}
      <RecentlyViewed />

      {/* Feature Cards */}
      <section className="mt-16 mb-10 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        {featureCards.map((card, i) => (
          <div key={i} className="flex flex-col items-center p-6 border rounded-lg shadow-sm">
            <div className="text-3xl text-black mb-4 bg-gray-100 p-4 rounded-full">{card.icon}</div>
            <h4 className="font-bold mb-2 text-sm">{card.title}</h4>
            <p className="text-xs text-gray-500">{card.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
};

export default Home;