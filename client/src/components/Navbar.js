import React, { useContext } from "react";
import { NavLink } from "react-router-dom";
import Logo from "./Logo";
import { AuthContext } from "../context/AuthContext";
import NotificationBadge from "../pages/NotificationBadge";
import "../styles/Navbar.css";

const Navbar = () => {
  const { user } = useContext(AuthContext);

  return (
    <nav className="navbar">
      <Logo />
      <ul>
        <li>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Home
          </NavLink>
        </li>

        {user && (
          <>
            <li>
              <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
                Dashboard
              </NavLink>
            </li>
            <li className="notification-item">
              <NavLink to="/notifications" className={({ isActive }) => (isActive ? "active" : "")}>
                <span className="nav-text">Notifications</span>
                <span className="notification-wrapper">
                  <NotificationBadge />
                </span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/prediction" className={({ isActive }) => (isActive ? "active" : "")}>
                Tank Predictions
              </NavLink>
            </li>
            <li>
              <NavLink to="/settings" className={({ isActive }) => (isActive ? "active" : "")}>
                Settings
              </NavLink>
            </li>
          </>
        )}

        {user?.role === "Admin" && (
          <li>
            <NavLink to="/usermanagement" className={({ isActive }) => (isActive ? "active" : "")}>
              User Management
            </NavLink>
          </li>
        )}
        {user?.role === "Admin" && (
          <li>
            <NavLink to="/allusersnotifications" className={({ isActive }) => (isActive ? "active" : "")}>
              Users Notifications
            </NavLink>
          </li>
        )}

        {user && (
          <li>
            <NavLink to="/logout" className={({ isActive }) => (isActive ? "active" : "")}>
              Logout
            </NavLink>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
