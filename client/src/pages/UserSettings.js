import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/UserSettings.css';

const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;

const UserSettings = () => {
  const [receiveEmailAlerts, setReceiveEmailAlerts] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user } = useContext(AuthContext);

  useEffect(() => {
    if (user) {
      fetchSettings();
    }
  }, [user]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/user/email-alerts`, {
        method: 'GET',
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
    } finally {
      setLoading(false);
    }
  };

  const toggleEmailAlerts = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/user/email-alerts`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to update email alerts');
      }

      const data = await response.json();
      setReceiveEmailAlerts(data.receive_email_alerts);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>Please log in to view settings.</div>;
  }

  return (
    <div className="user-settings-container">
      <h2>Notification Settings</h2>

      {error && (
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <p>{error}</p>
          <button onClick={fetchSettings} className="retry-button">
            Retry
          </button>
        </div>
      )}

      <div className="setting-item">
        <span>Email Alerts:</span>
        <button
          className={`toggle-switch ${receiveEmailAlerts ? 'on' : 'off'}`}
          onClick={toggleEmailAlerts}
          disabled={loading}
        >
          <div className="toggle-knob"></div>
          <span className="toggle-state">{loading ? '...' : receiveEmailAlerts ? 'ON' : 'OFF'}</span>
        </button>
      </div>

      <p className="setting-description">
        {receiveEmailAlerts
          ? "You'll receive email notifications for important alerts"
          : 'Email notifications are currently disabled'}
      </p>
    </div>
  );
};

export default UserSettings;
