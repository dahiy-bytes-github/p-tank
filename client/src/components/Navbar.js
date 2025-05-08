import React, { useContext, useState } from "react";
import { NavLink } from "react-router-dom";
import Logo from "./Logo";
import { AuthContext } from "../context/AuthContext";
import NotificationBadge from "../pages/NotificationBadge";
import "../styles/Navbar.css";

const Navbar = () => {
  const { user } = useContext(AuthContext);
  const [adminDropdownOpen, setAdminDropdownOpen] = useState(false);

  return (
    <nav className="navbar">
      <Logo />
      <ul className="nav-links">
        <li>
          <NavLink to="/" end>Home</NavLink>
        </li>

        {user && (
          <>
            <li><NavLink to="/dashboard">Dashboard</NavLink></li>
            <li><NavLink to="/prediction">Tank Predictions</NavLink></li>
            <li><NavLink to="/settings">Settings</NavLink></li>

            {user.role === "Admin" && (
              <li 
                className="dropdown" 
                onMouseEnter={() => setAdminDropdownOpen(true)}
                onMouseLeave={() => setAdminDropdownOpen(false)}
              >
                <span className="dropdown-toggle">Admin ▾</span>
                {adminDropdownOpen && (
                  <ul className="dropdown-menu">
                    <li><NavLink to="/usermanagement">User Management</NavLink></li>
                    <li><NavLink to="/allusersnotifications">Users Notifications</NavLink></li>
                  </ul>
                )}
              </li>
            )}
            
            <li className="notification-item">
              <NavLink to="/notifications">
                <span className="nav-text">Notifications</span>
                <NotificationBadge />
              </NavLink>
            </li>
            <li className="logout-item">
              <NavLink to="/logout">Logout</NavLink>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;