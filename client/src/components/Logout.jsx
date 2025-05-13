import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Logout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    const result = await logout();
    if (result.success) {
      navigate('/login');
    } else {
      console.error('Logout failed:', result.error);
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="text-white bg-red-500 hover:bg-red-600 px-4 py-2 rounded-md"
    >
      Logout
    </button>
  );
};

export default Logout;
