import { useState, useContext, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { validateUsername, validatePassword } from '../utils/validation';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, user } = useAuth();
  const { fetchCartItems } = useContext(CartContext);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [formErrors, setFormErrors] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  
  // Get the path the user was trying to access before being redirected to login
  const from = location.state?.from?.pathname || '/';
  
  // Redirect if user is already logged in
  useEffect(() => {
    if (isAuthenticated() && user) {
      navigate(from);
    }
  }, [isAuthenticated, user, navigate, from]);

  const handleGoogleLogin = () => {
    // TODO: Implement actual Google authentication
    console.log('Google login clicked');
  };

  // Email verification state removed

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    // Validate username
    const usernameValidation = validateUsername(formData.username);
    if (!usernameValidation.isValid) {
      errors.username = usernameValidation.message;
    }
    
    // Validate password
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      errors.password = passwordValidation.message;
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      return;
    }
    
    try {
      setNotification({ message: 'Logging in...', type: 'info' });
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        setNotification({ message: 'Login successful', type: 'success' });
        
        try {
          // Fetch cart items to trigger the cart synchronization
          // Fetch cart items to trigger the cart synchronization
          await fetchCartItems();
          
          // Navigate to the page the user was trying to access, or home if none
          setTimeout(() => navigate(from), 1000);
        } catch (cartError) {
          console.error('Error fetching cart items:', cartError);
          // Still navigate even if cart fetch fails
          setTimeout(() => navigate(from), 1000);
        }
      } else {
        setNotification({ message: result.error || 'Login failed. Please check your credentials.', type: 'error' });
      }
    } catch (error) {
      console.error('Login error:', error);
      setNotification({ 
        message: error.response?.data?.error || error.message || 'Login failed. Please try again later.', 
        type: 'error' 
      });
    }
  };
  // Email verification resend function removed

  return (
    <div className="min-h-screen bg-white flex flex-col justify-between">
      {notification.message && (
        <div
          className={`notification ${notification.type} p-4 mb-4 text-center rounded-md shadow-md ${
            notification.type === 'success' ? 'bg-green-100 text-green-800' : 
            notification.type === 'info' ? 'bg-blue-100 text-blue-800' : 
            notification.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
            'bg-red-100 text-red-800'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row items-center justify-center p-6 lg:p-16">
        {/* Image Side */}
        <div className="hidden lg:block w-full lg:w-1/2 p-6">
          <img
            src="/shopping-mobile-cart.avif"
            alt="Shopping Visual"
            className="w-full max-w-md mx-auto"
          />
        </div>

        {/* Login Form */}
        <div className="w-full lg:w-1/2 max-w-md">
          <h2 className="text-3xl font-semibold mb-2">Welcome Back</h2>
          <p className="text-gray-600 mb-6">Enter your credentials below</p>
          
          {/* Google Login Button */}
          <button
            onClick={handleGoogleLogin}
            className="w-full border border-gray-300 py-2 px-4 rounded-md mb-4 flex items-center justify-center gap-2 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or</span>
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleLogin}>
            <div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Username"
                className={`w-full border-b ${formErrors.username ? 'border-red-500' : 'border-gray-300'} py-2 focus:outline-none`}
              />
              {formErrors.username && (
                <p className="text-red-500 text-xs mt-1">{formErrors.username}</p>
              )}
            </div>
            <div>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Password"
                className={`w-full border-b ${formErrors.password ? 'border-red-500' : 'border-gray-300'} py-2 focus:outline-none`}
              />
              {formErrors.password && (
                <p className="text-red-500 text-xs mt-1">{formErrors.password}</p>
              )}
            </div>
            <div className="flex justify-between items-center">
              <label className="inline-flex items-center">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-red-500" />
                <span className="ml-2 text-gray-700 text-sm">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-sm text-red-500 hover:underline">Forgot Password?</Link>
            </div>
            <button
              type="submit"
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-md w-full"
            >
              Log In
            </button>
            <p className="text-center text-sm mt-4">
              Don't have an account?{' '}
              <Link to="/register" className="text-red-500 hover:underline">Sign Up</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
