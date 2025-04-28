import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/NotificationList.css';

const NotificationList = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/notifications', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }
      
      const data = await response.json();
      setNotifications(data.notifications);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5555/notifications/${id}/read`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to mark as read');
      }
      
      setNotifications(prev =>
        prev.map(notification =>
          notification.id === id ? { ...notification, is_read: true } : notification
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/notifications/read-all', {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to mark all as read');
      }
      
      setNotifications(prev =>
        prev.map(notification => ({ ...notification, is_read: true }))
      );
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading notifications...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p>{error}</p>
        <button onClick={fetchNotifications} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="notification-list-container">
      <div className="notification-header">
        <h2>Notifications</h2>
        {notifications.some(n => !n.is_read) && (
          <button 
            onClick={markAllAsRead} 
            className="mark-all-button"
          >
            Mark All as Read
          </button>
        )}
      </div>
      
      {notifications.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p>No notifications yet</p>
          <p className="empty-subtext">We'll notify you when there's new activity</p>
        </div>
      ) : (
        <ul className="notification-list">
          {notifications.map((notification) => (
            <li 
              key={notification.id} 
              className={`notification-item ${notification.is_read ? 'read' : 'unread'}`}
            >
              <div className="notification-content">
                <p className="notification-message">{notification.message}</p>
                <p className="notification-time">{new Date(notification.created_at).toLocaleString()}</p>
              </div>
              {!notification.is_read && (
                <button 
                  onClick={() => markAsRead(notification.id)} 
                  className="mark-read-button"
                >
                  ✓ Mark as Read
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default NotificationList;