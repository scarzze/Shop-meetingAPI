import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import FloatingContactButton from './components/contact';
import ScrollToTop from './components/ScrollToTop';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import ProductDetail from './pages/ProductDetail';
import Checkout from './pages/Checkout';
import Cart from './pages/Cart';
import About from './pages/About';
import NotFound from './pages/NotFound';
import Wishlist from './pages/Wishlist';
import Contact from './pages/Contact';
import Products from './pages/Products';
import CategoryProducts from './pages/CategoryProducts';
import FaqPage from './pages/FaqPage';
import SearchResults from './pages/SearchResults';


const App = () => {

  return (
    <ErrorBoundary>
      <div>
        <ScrollToTop />
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/products" element={<Products />} />
          <Route path="/category/:category" element={<CategoryProducts />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/about" element={<About />} />
          <Route path="/wishlist" element={<ProtectedRoute><Wishlist /></ProtectedRoute>} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/faq" element={<FaqPage />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <Footer />
        <FloatingContactButton />
      </div>
    </ErrorBoundary>
  );
};

export default App;
