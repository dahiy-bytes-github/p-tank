
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
      const response = await fetch('http://localhost:5555/notifications', { // Adjusted URL
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
      const response = await fetch(`http://localhost:5555/notifications/${id}/read`, { // Adjusted URL
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to mark as read');
      }
      // Update state to reflect the change
      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === id ? { ...notification, is_read: true } : notification
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading notifications...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="notification-list-container">
      <h2>Notifications</h2>
      {notifications.length === 0 ? (
        <div>No notifications</div>
      ) : (
        <ul>
          {notifications.map((notification) => (
            <li key={notification.id} className={`notification-item ${notification.is_read ? 'read' : 'unread'}`}>
              <p>{notification.message}</p>
              {!notification.is_read && (
                <button onClick={() => markAsRead(notification.id)}>Mark as Read</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default NotificationList;
