import React, { useEffect, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileForm from '../components/ProfileForm';
import AddressBook from '../components/AddressBook';
import PaymentOptions from '../components/PaymentOptions';
import MyOrders from '../components/MyOrders';
import MyReturns from '../components/MyReturns';
import MyCancellations from '../components/MyCancellations';
import MyWishlist from '../components/MyWishlist';
import { AuthContext } from '../context/AuthContext';

const Profile = () => {
  const { user, loading, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [activeSection, setActiveSection] = useState('profile');
  
  useEffect(() => {
    document.title = 'Profile - Shop Meeting';
  }, []);
  
  useEffect(() => {
    // Check if user is authenticated
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);
  
  const handleLogout = async () => {
    try {
      const result = await logout();
      if (result.success) {
        setNotification({ message: 'Logged out successfully', type: 'success' });
        setTimeout(() => navigate('/'), 1000);
      } else {
        setNotification({ message: result.error || 'Logout failed', type: 'error' });
      }
    } catch (error) {
      setNotification({ message: 'Logout failed', type: 'error' });
    }
  };

  // Render the appropriate component based on the active section
  const renderActiveSection = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">Edit Your Profile</h2>
            <ProfileForm />
          </>
        );
      case 'address':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">Address Book</h2>
            <AddressBook />
          </>
        );
      case 'payment':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">My Payment Options</h2>
            <PaymentOptions />
          </>
        );
      case 'orders':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">My Orders</h2>
            <MyOrders />
          </>
        );
      case 'returns':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">My Returns</h2>
            <MyReturns />
          </>
        );
      case 'cancellations':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">My Cancellations</h2>
            <MyCancellations />
          </>
        );
      case 'wishlist':
        return (
          <>
            <h2 className="text-xl font-semibold text-red-500 mb-6">My Wishlist</h2>
            <MyWishlist />
          </>
        );
      default:
        return <ProfileForm />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {notification.message && (
        <div
          className={`notification ${notification.type} p-4 mb-4 text-center rounded-md shadow-md ${
            notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Main Container */}
      <div className="flex flex-col lg:flex-row p-6 lg:p-16 gap-6">
        {/* Sidebar */}
        <aside className="w-full lg:w-1/4 border-r border-gray-200 pr-6">
          <h3 className="text-lg font-semibold mb-4">Manage My Profile</h3>
          <ul className="space-y-2 text-gray-600">
            <li 
              className={`cursor-pointer ${activeSection === 'profile' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('profile')}
            >
              My Profile
            </li>
            <li 
              className={`cursor-pointer ${activeSection === 'address' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('address')}
            >
              Address Book
            </li>
            <li 
              className={`cursor-pointer ${activeSection === 'payment' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('payment')}
            >
              My Payment Options
            </li>
          </ul>
          
          <h3 className="text-lg font-semibold mt-6 mb-4">My Orders</h3>
          <ul className="space-y-2 text-gray-600">
            <li 
              className={`cursor-pointer ${activeSection === 'orders' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('orders')}
            >
              My Orders
            </li>
            <li 
              className={`cursor-pointer ${activeSection === 'returns' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('returns')}
            >
              My Returns
            </li>
            <li 
              className={`cursor-pointer ${activeSection === 'cancellations' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('cancellations')}
            >
              My Cancellations
            </li>
          </ul>
          
          <h3 className="text-lg font-semibold mt-6 mb-4">My Lists</h3>
          <ul className="space-y-2 text-gray-600">
            <li 
              className={`cursor-pointer ${activeSection === 'wishlist' ? 'text-red-500 font-semibold' : 'hover:text-black'}`}
              onClick={() => setActiveSection('wishlist')}
            >
              My Wishlist
            </li>
          </ul>
          
          <div className="mt-10">
            <button
              onClick={handleLogout}
              className="w-full bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-md transition-colors"
            >
              Log Out
            </button>
          </div>
        </aside>

        {/* Content Section */}
        <section className="w-full lg:w-3/4 bg-gray-50 p-8 rounded-md shadow-sm">
          {renderActiveSection()}
        </section>
      </div>
    </div>
  );
};

export default Profile;
