import { useState, useContext, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { validateUsername, validatePassword, isValidEmail } from '../utils/validation';
import api from '../utils/axiosConfig';
import { SERVICE_ENDPOINTS } from '../utils/apiConfig';

const Register = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, user } = useAuth();
  const { fetchCartItems } = useContext(CartContext);
  
  // Get the path the user was trying to access before being redirected to register
  const from = location.state?.from?.pathname || '/';
  
  // Redirect if user is already logged in
  useEffect(() => {
    if (isAuthenticated() && user) {
      navigate(from);
    }
  }, [isAuthenticated, user, navigate, from]);
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [formErrors, setFormErrors] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleGoogleSignUp = () => {
    // TODO: Implement actual Google authentication
    console.log('Google sign-up clicked');
  };

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
    
    // Validate email
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Validate password
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      errors.password = passwordValidation.message;
    }
    
    // Validate password confirmation
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      return;
    }
    
    const data = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
    };

    try {
      setNotification({ message: 'Creating your account...', type: 'info' });
      
      // Register the user
      const response = await api.post(`${SERVICE_ENDPOINTS.AUTH}/register`, data);
      setNotification({ message: 'Registration successful! Logging you in...', type: 'success' });
      
      // Automatically log in the user after successful registration
      try {
        const loginResult = await login(data.username, data.password);
        
        if (loginResult.success) {
          try {
            // Fetch cart items to trigger the cart synchronization
            await fetchCartItems();
            
            // Navigate to home page
            setTimeout(() => navigate('/'), 1000);
          } catch (cartError) {
            console.error('Error fetching cart items:', cartError);
            // Still navigate even if cart fetch fails
            setTimeout(() => navigate('/'), 1000);
          }
        } else {
          console.error('Auto-login failed after registration:', loginResult.error);
          // If login fails, redirect to login page
          setNotification({ message: 'Account created but automatic login failed. Please log in manually.', type: 'warning' });
          setTimeout(() => navigate('/login'), 1500);
        }
      } catch (loginError) {
        console.error('Auto-login failed after registration:', loginError);
        // If auto-login fails, redirect to login page
        setNotification({ message: 'Account created but automatic login failed. Please log in manually.', type: 'warning' });
        setTimeout(() => navigate('/login'), 1500);
      }
    } catch (error) {
      console.error('Registration error:', error);
      if (error.response?.status === 409) { // Conflict status code for existing user
        setNotification({ message: 'User already exists. Please log in.', type: 'error' });
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setNotification({ 
          message: error.response?.data?.error || 'Registration failed. Please try again.', 
          type: 'error' 
        });
      }
    }
  };

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

        {/* Register Form */}
        <div className="w-full lg:w-1/2 max-w-md">
          <h2 className="text-3xl font-semibold mb-2">Create an Account</h2>
          <p className="text-gray-600 mb-6">Enter your details below</p>
          
          {/* Google Sign Up Button */}
          <button
            onClick={handleGoogleSignUp}
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
            Sign up with Google
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or</span>
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleRegister}>
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
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                className={`w-full border-b ${formErrors.email ? 'border-red-500' : 'border-gray-300'} py-2 focus:outline-none`}
              />
              {formErrors.email && (
                <p className="text-red-500 text-xs mt-1">{formErrors.email}</p>
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
            <div>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm Password"
                className={`w-full border-b ${formErrors.confirmPassword ? 'border-red-500' : 'border-gray-300'} py-2 focus:outline-none`}
              />
              {formErrors.confirmPassword && (
                <p className="text-red-500 text-xs mt-1">{formErrors.confirmPassword}</p>
              )}
            </div>
            <button
              type="submit"
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-md w-full"
            >
              Create Account
            </button>
            <p className="text-center text-sm mt-4">
              Already have an account?{' '}
              <Link to="/login" className="text-red-500 hover:underline">Log In</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
