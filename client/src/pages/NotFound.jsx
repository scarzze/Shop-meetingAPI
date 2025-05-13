import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-6 text-center min-h-[70vh]">
      {/* Breadcrumb */}
      <div className="text-sm text-gray-500 mb-6">
        <span className="mr-1">Home</span> / <span className="ml-1">404 Error</span>
      </div>

      {/* 404 Content */}
      <h1 className="text-6xl font-bold mb-4">404 Not Found</h1>
      <p className="text-gray-600 text-lg mb-8">
        Your visited page not found. You may go home page.
      </p>

      <Link
        to="/"
        className="px-6 py-3 bg-red-500 text-white rounded hover:bg-red-600 transition"
      >
        Back to home page
      </Link>
    </div>
  );
};

export default NotFound;
