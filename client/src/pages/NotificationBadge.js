
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/NotificationBadge.css';

const NotificationBadge = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState('');
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchUnreadCount();
    const intervalId = setInterval(fetchUnreadCount, 60000); // Refresh every minute

    return () => clearInterval(intervalId); // Clean up interval
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/notifications/unread-count', { // Adjusted URL
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch unread count');
      }
      const data = await response.json();
      setUnreadCount(data.unread_count);
    } catch (err) {
      setError(err.message);
    }
  };

  if (error) return <span className="error-badge">Error</span>;

  return (
    <div className="notification-badge">
      {unreadCount > 0 && <span className="badge-count">{unreadCount}</span>}
    </div>
  );
};

export default NotificationBadge;
