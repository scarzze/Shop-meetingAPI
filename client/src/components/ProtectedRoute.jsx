import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, loading, error } = useAuth();
  const location = useLocation();

  // Show loading indicator while checking authentication status
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }
  
  // Show authentication error
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full">
          <div className="text-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-red-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-800 mt-4">Authentication Error</h2>
          </div>
          <p className="text-gray-600 mb-6">
            {error}
          </p>
          <div className="flex flex-col space-y-2">
            <button
              onClick={() => window.location.href = '/login'}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors"
            >
              Log In
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="w-full border border-gray-300 text-gray-700 py-2 rounded hover:bg-gray-100 transition-colors"
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  return user ? children : <Navigate to="/login" state={{ from: location }} />;
};

export default ProtectedRoute;