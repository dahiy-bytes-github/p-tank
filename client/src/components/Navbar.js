import React, { useContext, useState } from "react";
import { NavLink } from "react-router-dom";
import Logo from "./Logo";
import { AuthContext } from "../context/AuthContext";
import NotificationBadge from "../pages/NotificationBadge";
import "../styles/Navbar.css";

const Navbar = () => {
  const { user } = useContext(AuthContext);
  const [adminDropdownOpen, setAdminDropdownOpen] = useState(false);

  const toggleAdminDropdown = () => {
    setAdminDropdownOpen(!adminDropdownOpen);
  };

  return (
    <nav className="navbar">
      <Logo />
      <ul className="nav-links">
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

            {/* Admin Dropdown */}
            {user.role === "Admin" && (
              <li className="dropdown" onMouseEnter={toggleAdminDropdown} onMouseLeave={toggleAdminDropdown}>
                <span className="dropdown-toggle">Admin ▾</span>
                {adminDropdownOpen && (
                  <ul className="dropdown-menu">
                    <li>
                      <NavLink to="/usermanagement" className={({ isActive }) => (isActive ? "active" : "")}>
                        User Management
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/allusersnotifications" className={({ isActive }) => (isActive ? "active" : "")}>
                        Users Notifications
                      </NavLink>
                    </li>
                  </ul>
                )}
              </li>
            )}
            <li className="notification-item">
              <NavLink to="/notifications" className={({ isActive }) => (isActive ? "active" : "")}>
                <span className="nav-text">Notifications</span>
                <NotificationBadge />
              </NavLink>
            </li>
            <li>
              <NavLink to="/logout" className={({ isActive }) => (isActive ? "active" : "")}>
                Logout
              </NavLink>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
