import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const VerifyEmail = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { verifyEmail } = useAuth();
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('Verifying your email...');

  useEffect(() => {
    const verifyUserEmail = async () => {
      // Get token from URL query params
      const queryParams = new URLSearchParams(location.search);
      const token = queryParams.get('token');

      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const result = await verifyEmail(token);
        
        if (result.success) {
          setStatus('success');
          setMessage('Your email has been successfully verified! You can now log in to your account.');
        } else {
          setStatus('error');
          setMessage(result.error || 'Verification failed. The link may have expired or is invalid.');
        }
      } catch (error) {
        setStatus('error');
        setMessage('An error occurred during verification. Please try again later.');
      }
    };

    verifyUserEmail();
  }, [location.search, verifyEmail]);

  const handleRedirect = () => {
    navigate(status === 'success' ? '/login' : '/register');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Email Verification</h2>
          
          {status === 'verifying' && (
            <div className="mt-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">{message}</p>
            </div>
          )}
          
          {status === 'success' && (
            <div className="mt-8">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <p className="mt-4 text-green-600 font-medium">{message}</p>
            </div>
          )}
          
          {status === 'error' && (
            <div className="mt-8">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <p className="mt-4 text-red-600 font-medium">{message}</p>
            </div>
          )}
          
          <div className="mt-8">
            <button
              onClick={handleRedirect}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-500 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              {status === 'success' ? 'Go to Login' : 'Go to Registration'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
