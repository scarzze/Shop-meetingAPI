import React, { useContext, useState } from 'react';
import { FiShoppingCart, FiHeart, FiUser, FiSearch } from 'react-icons/fi';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeadset } from '@fortawesome/free-solid-svg-icons';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { WishlistContext } from '../context/WishlistContext';

const Navbar = () => {
  const { isAuthenticated } = useContext(AuthContext);
  const { cartItems } = useContext(CartContext);
  const { wishlistItems } = useContext(WishlistContext);
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  
  const handleProfileClick = (e) => {
    e.preventDefault();
    if (isAuthenticated()) {
      navigate('/profile');
    } else {
      navigate('/login', { state: { from: '/profile' } });
    }
  };
  
  const handleWishlistClick = (e) => {
    e.preventDefault();
    if (isAuthenticated()) {
      navigate('/wishlist');
    } else {
      navigate('/login', { state: { from: '/wishlist' } });
    }
  };
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };
  return (
    <header className="bg-white border-b sticky top-0 z-50">
      {/* Top banner */}
      <div className="bg-black text-white text-sm text-center py-2">
        Mid-year Sales for All Laptops And Free Express Delivery - OFF 50%!&nbsp;
        <a href="/" className="underline font-semibold hover:text-gray-300">ShopNow</a>
      </div>

      {/* Main navbar */}
      <div className="max-w-7xl mx-auto flex items-center justify-between py-4 px-4">
        <div className="text-2xl font-bold">ShopMeeting</div>

        <nav className="hidden md:flex gap-6 text-gray-700 font-medium">
          <Link to="/" className="hover:text-black transition">Home</Link>
          <Link to="/about" className="hover:text-black transition">About</Link>
          <Link to="/wishlist" className="hover:text-black transition">Wishlist</Link>
          {!isAuthenticated() && (
            <Link to="/register" className="hover:text-black transition">Sign Up</Link>
          )}
        </nav>

        <div className="flex items-center gap-6">
          {/* Search input */}
          <form onSubmit={handleSearch} className="relative hidden md:block">
            <input
              type="text"
              placeholder="Search products or categories"
              className="border rounded-full px-4 py-1.5 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-black transition w-64"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button 
              type="submit" 
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-black focus:outline-none"
            >
              <FiSearch className="w-4 h-4" />
            </button>
          </form>

          {/* Icons */}
          <div className="flex gap-4 items-center text-gray-700">
            <a href="#" onClick={handleWishlistClick} className="relative">
              <FiHeart className="w-5 h-5 cursor-pointer transition-colors duration-200 hover:text-red-500" />
              {wishlistItems.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {wishlistItems.length}
                </span>
              )}
            </a>
            <Link to="/cart" className="relative">
              <FiShoppingCart className="w-5 h-5 cursor-pointer transition-colors duration-200 hover:text-red-500" />
              {cartItems.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {cartItems.length}
                </span>
              )}
            </Link>
            <a href="#" onClick={handleProfileClick}>
              <FiUser className="w-5 h-5 cursor-pointer transition-colors duration-200 hover:text-red-500" />
            </a>
            <Link to="/contact">
              <FontAwesomeIcon icon={faHeadset} className="w-5 h-5 cursor-pointer transition-colors duration-200 hover:text-red-500" />
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
