
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/UserSettings.css';

const UserSettings = () => {
  const [receiveEmailAlerts, setReceiveEmailAlerts] = useState(true);
  const [error, setError] = useState('');
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/user/toggle-email-alerts', { // Assuming a profile endpoint
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }
      const data = await response.json();
      setReceiveEmailAlerts(data.receive_email_alerts);
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleEmailAlerts = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:5555/user/toggle-email-alerts', { // Adjusted URL
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to toggle email alerts');
      }

      const data = await response.json();
      setReceiveEmailAlerts(data.receive_email_alerts);
    } catch (err) {
      setError(err.message);
    }
  };

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="user-settings-container">
      <h2>User Settings</h2>
      <label>
        Receive Email Alerts:
        <input
          type="checkbox"
          checked={receiveEmailAlerts}
          onChange={toggleEmailAlerts}
        />
      </label>
    </div>
  );
};

export default UserSettings;
