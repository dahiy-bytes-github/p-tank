import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import "../styles/GetAllUsersNotifications.css";

const apiBaseUrl = process.env.REACT_APP_API_BASE_URL;

const GetAllUsersNotifications = () => {
  const { user } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNotifications = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          setError("No access token found. Please log in.");
          setLoading(false);
          return;
        }
        const res = await fetch(`${apiBaseUrl}/notifications/all`, {
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          credentials: 'include'
        });
        if (!res.ok) {
          throw new Error("Failed to fetch notifications");
        }
        const data = await res.json();
        setNotifications(data.notifications || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchNotifications();
  }, []);

  // Optional: Restrict to admins
  if (!user || user.role !== "Admin") {
    return <div className="notif-error">Admin access only.</div>;
  }

  if (loading) return <div className="notif-loading" aria-live="polite">Loading notifications...</div>;
  if (error) return <div className="notif-error" aria-live="polite">Error: {error}</div>;
  if (notifications.length === 0) return <div className="notif-empty">No notifications found.</div>;

  return (
    <div className="notifications-list">
      <h2>All Notifications</h2>
      <ul>
        {notifications.map((notif) => (
          <li
            key={notif.notification_id + "-" + notif.user_id}
            className={notif.is_read ? "notification read" : "notification unread"}
          >
            <div className="notif-header">
              <span className="notif-type">{notif.notification_type}</span>
              <span className={`notif-severity ${notif.severity}`}>{notif.severity}</span>
            </div>
            <div className="notif-message">{notif.message}</div>
            <div className="notif-meta">
              <span className="notif-date">
                {new Date(notif.created_at).toLocaleString()}
              </span>
              <span className="notif-status">
                {notif.is_read ? "Read" : "Unread"}
              </span>
              <span className="notif-user">{notif.user_email}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GetAllUsersNotifications;
