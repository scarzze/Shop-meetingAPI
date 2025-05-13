import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeadset } from '@fortawesome/free-solid-svg-icons';

const FloatingContactButton = () => {
  const location = useLocation();

  if (location.pathname === '/contact') {
    return null;
  }

  return (
    <Link
      to="/contact"
      className="fixed bottom-10 right-10 bg-black text-white p-4 rounded-full shadow-lg hover:bg-gray-800 transition"
      aria-label="Contact Support"
      role="button"
      title="Contact Support"
    >
      <FontAwesomeIcon icon={faHeadset} size="lg" aria-hidden="true" />
    </Link>
  );
};

export default FloatingContactButton;
