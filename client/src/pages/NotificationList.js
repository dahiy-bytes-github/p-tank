import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/NotificationList.css';

const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;

const NotificationList = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/notifications`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (!response.ok) throw new Error('Failed to fetch notifications');
      
      const { notifications } = await response.json();
      setNotifications(notifications);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (userNotificationId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${apiBaseUrl}/notifications/${userNotificationId}/read`, 
        {
          method: 'PATCH',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Failed to mark as read');
      
      const updatedNotification = await response.json();
      
      setNotifications(prev =>
        prev.map(n => 
          n.user_notification_id === updatedNotification.user_notification_id 
            ? { ...n, ...updatedNotification } 
            : n
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/notifications/read-all`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to mark all as read');
      
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      );
    } catch (err) {
      setError(err.message);
    }
  };

  // Render loading/error states...

  return (
    <div className="notification-list-container">
      <div className="notification-header">
        <h2>Notifications</h2>
        {notifications.some(n => !n.is_read) && (
          <button onClick={markAllAsRead} className="mark-all-button">
            Mark All as Read
          </button>
        )}
      </div>
      
      {notifications.length === 0 ? (
        <div className="empty-state">No notifications yet</div>
      ) : (
        <ul className="notification-list">
          {notifications.map((notification) => (
            <li 
              key={notification.user_notification_id} 
              className={`notification-item ${notification.is_read ? 'read' : 'unread'}`}
            >
              <div className="notification-content">
                <p className="notification-message">{notification.message}</p>
                <p className="notification-time">
                  {new Date(notification.created_at).toLocaleString()}
                  {notification.is_read && (
                    <span className="read-time">
                      · Read at {new Date(notification.read_at).toLocaleTimeString()}
                    </span>
                  )}
                </p>
              </div>
              {!notification.is_read && (
                <button 
                  onClick={() => markAsRead(notification.user_notification_id)}
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