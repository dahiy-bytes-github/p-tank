import React, { useContext } from "react";
import { NavLink } from "react-router-dom";
import Logo from "./Logo";
import { AuthContext } from "../context/AuthContext";
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

        {/* Dashboard (visible to all logged-in users) */}
        {user && (
          <li>
            <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
              Dashboard
            </NavLink>
          </li>
        )}

        {/* User Management (Admin only) */}
        {user?.role === "Admin" && (
          <li>
            <NavLink to="/usermanagement" className={({ isActive }) => (isActive ? "active" : "")}>
              User Management
            </NavLink>
          </li>
        )}

        {/* Logout (visible to all logged-in users) */}
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