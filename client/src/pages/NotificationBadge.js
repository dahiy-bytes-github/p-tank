import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/NotificationBadge.css';

const NotificationBadge = ({ onClick }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useContext(AuthContext);

  const fetchUnreadCount = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/notifications/unread-count', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch notification count');
      }

      const data = await response.json();
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error('Notification count error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUnreadCount();
    
    // Set up polling every 30 seconds
    const intervalId = setInterval(fetchUnreadCount, 30000);
    
    return () => clearInterval(intervalId);
  }, [user]);

  if (error) {
    return (
      <div className="notification-error" title="Notification error">
        !
      </div>
    );
  }

  return (
    <div 
      className="notification-badge-container" 
      onClick={onClick}
      aria-label={`${unreadCount} unread notifications`}
    >
      <svg className="bell-icon" viewBox="0 0 24 24">
        <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
      </svg>
      
      {unreadCount > 0 && (
        <span className={`badge-count ${unreadCount > 9 ? 'double-digit' : ''}`}>
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {loading && !unreadCount && (
        <span className="loading-dot"></span>
      )}
    </div>
  );
};

export default NotificationBadge;