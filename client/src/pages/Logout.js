import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const logout = async () => {
      try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch('http://localhost:5555/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include' // Important for CORS
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Logout failed');
        }

        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Redirect to login
        navigate('/login');
      } catch (err) {
        console.error('Logout error:', err);
        // Fallback redirect if logout fails
        navigate('/');
      }
    };

    logout();
  }, [navigate]);

  return (
    <div className="logout-container">
      <p>Logging out...</p>
    </div>
  );
};

export default Logout;