import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-black text-white py-10 px-6">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8">
        {/* Brand */}
        <div>
          <h3 className="text-xl font-bold mb-2">ShopMeeting</h3>
          <p className="text-sm mb-4">Subscribe</p>
          <p className="text-xs text-gray-300">Get 10% off your first order</p>
          <div className="mt-2">
            <input
              type="email"
              placeholder="Enter your email"
              className="p-2 text-black rounded-l-md"
            />
            <button className="bg-red-500 px-3 py-2 rounded-r-md text-white">→</button>
          </div>
        </div>

        {/* Support */}
        <div>
          <h4 className="font-semibold mb-2">Support</h4>
          <p className="text-sm text-gray-300">Ngong Road, Nairobi - Kenya</p>
          <p className="text-sm text-gray-300">customer@ShopMeet.com</p>
          <p className="text-sm text-gray-300">+254722222256</p>
        </div>

        {/* Account */}
        <div>
          <h4 className="font-semibold mb-2">Account</h4>
          <ul className="space-y-1 text-sm text-gray-300">
            <li><a href="/profile">My Account</a></li>
            <li><a href="/login">Login / Register</a></li>
            <li><a href="/cart">Cart</a></li>
            <li><a href="/wishlist">Wishlist</a></li>
            <li><a href="/">Shop</a></li>
          </ul>
        </div>

        {/* Quick Link */}
        <div>
          <h4 className="font-semibold mb-2">Quick Link</h4>
          <ul className="space-y-1 text-sm text-gray-300">
            <li><a href="#">Privacy Policy</a></li>
            <li><a href="#">Terms Of Use</a></li>
            <li><a href="#">FAQ</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>

        {/* App Download */}
        <div>
          <h4 className="font-semibold mb-2">Download App</h4>
          <p className="text-xs text-gray-400 mb-2">Save KES 300 with App, New User Only</p>
          <p className="text-xs text-gray-400 mb-2">App Coming Soon...</p>
          {/* <div className="space-y-2">
            <img src="/google-play-badge.png" alt="Google Play" className="w-28" />
            <img src="/app-store-badge.png" alt="App Store" className="w-28" />
          </div> */}
          <div className="flex space-x-4 mt-4 text-lg">
            <a href="#"><i className="fab fa-facebook-f"></i></a>
            <a href="#"><i className="fab fa-twitter"></i></a>
            <a href="#"><i className="fab fa-instagram"></i></a>
            <a href="#"><i className="fab fa-linkedin-in"></i></a>
          </div>
        </div>
      </div>

      <div className="text-center text-sm text-gray-500 mt-10 border-t pt-4">
        © Copyright ShopMeeting 2025. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
