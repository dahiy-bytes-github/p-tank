import React, { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Logout = () => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    logout();
    navigate('/'); // Immediate redirect
  }, [logout, navigate]); // Added dependencies

  return <div>Logging out...</div>;
};

export default Logout;
