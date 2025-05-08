import React, { useContext, useEffect, useState, useCallback } from "react";
import { AuthContext } from "../context/AuthContext";
import '../styles/UserManagement.css';

const FILTER_ROLES = ["All", "Admin", "Normal"];

const UserManagement = () => {
  const { user } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editedUser, setEditedUser] = useState({
    full_name: "",
    email: "",
    role: "Normal",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Filter states
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("All");

  // For delete confirmation dialog
  const [deleteCandidate, setDeleteCandidate] = useState(null);

  const accessToken = localStorage.getItem("access_token");

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:5555/users", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch users");
      }

      const data = await response.json();
      setUsers(data.users || []);
      setSuccess("Users loaded successfully");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  // Auto-dismiss success message after 4 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (user?.role === "Admin") {
      fetchUsers();
    }
  }, [user, fetchUsers]);

  const startEditing = (user) => {
    setEditingUserId(user.id);
    setEditedUser({
      full_name: user.full_name,
      email: user.email,
      role: user.role,
    });
    setError(null);
    setSuccess(null);
  };

  const cancelEditing = () => {
    setEditingUserId(null);
    setEditedUser({
      full_name: "",
      email: "",
      role: "Normal",
    });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditedUser((prev) => ({ ...prev, [name]: value }));
  };

  const saveEdit = async (id) => {
    setLoading(true);
    try {
      if (!['Admin', 'Normal'].includes(editedUser.role)) {
        throw new Error("Invalid role selected");
      }

      const response = await fetch(`http://localhost:5555/users/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(editedUser),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to update user");
      }

      await fetchUsers();
      cancelEditing();
      setSuccess("User updated successfully");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Show confirmation dialog instead of deleting immediately
  const requestDeleteUser = (user) => {
    setDeleteCandidate(user);
  };

  // Called only after confirmation
  const confirmDeleteUser = async () => {
    if (!deleteCandidate) return;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5555/users/${deleteCandidate.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to delete user");
      }

      await fetchUsers();
      setSuccess("User deleted successfully");
      setDeleteCandidate(null);
    } catch (error) {
      setError(error.message);
      setDeleteCandidate(null);
    } finally {
      setLoading(false);
    }
  };

  // Cancel deletion
  const cancelDeleteUser = () => {
    setDeleteCandidate(null);
  };

  // Filter logic: search + role
  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole =
      roleFilter === "All" ? true : u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  if (!user) {
    return (
      <div className="auth-message">
        <div className="message-icon">🔒</div>
        <h2>Authentication Required</h2>
        <p>Please log in to access the user management system.</p>
      </div>
    );
  }

  if (user.role !== "Admin") {
    return (
      <div className="auth-message">
        <div className="message-icon">🚫</div>
        <h2>Permission Denied</h2>
        <p>Your account does not have administrator privileges to access this page.</p>
      </div>
    );
  }

  return (
    <div className="user-management-container">
      <div className="management-header">
        <h1>User Management Dashboard</h1>
        <p className="management-subtitle">
          Manage system users and administrator privileges
        </p>
      </div>

      {/* Filter Controls */}
      <div className="filter-controls">
        <input
          type="text"
          placeholder="Search by name or email"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="search-input"
        />
        <select
          value={roleFilter}
          onChange={e => setRoleFilter(e.target.value)}
          className="role-dropdown"
        >
          {FILTER_ROLES.map(role => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
      </div>

      {loading && users.length === 0 && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading user data...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <p>{error}</p>
          <button onClick={fetchUsers} className="retry-button">
            Retry
          </button>
        </div>
      )}

      {success && (
        <div className="success-message">
          <div className="success-icon">✓</div>
          <p>{success}</p>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteCandidate && (
        <div className="custom-dialog-overlay">
          <div className="custom-dialog">
            <div className="dialog-title">Confirm Deletion</div>
            <div className="dialog-message">
              This user will be deleted permanently. Do you want to proceed?
            </div>
            <div className="dialog-actions">
              <button className="cancel-button" onClick={cancelDeleteUser} disabled={loading}>
                Cancel
              </button>
              <button className="delete-button" onClick={confirmDeleteUser} disabled={loading}>
                {loading ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

      {!loading && filteredUsers.length === 0 && !error && (
        <div className="empty-state">
          <p>No users found in the system.</p>
        </div>
      )}

      {filteredUsers.length > 0 && (
        <div className="user-table-container">
          <table className="user-table">
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className={user.role === "Admin" ? "admin-row" : ""}>
                  {editingUserId === user.id ? (
                    <>
                      <td>
                        <input
                          type="text"
                          name="full_name"
                          value={editedUser.full_name}
                          onChange={handleEditChange}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="email"
                          name="email"
                          value={editedUser.email}
                          onChange={handleEditChange}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <select
                          name="role"
                          value={editedUser.role}
                          onChange={handleEditChange}
                          className="role-select"
                        >
                          <option value="Normal">Normal</option>
                          <option value="Admin">Admin</option>
                        </select>
                      </td>
                      <td className="action-buttons">
                        <button 
                          onClick={() => saveEdit(user.id)} 
                          className="save-button"
                          disabled={loading}
                        >
                          {loading ? "Saving..." : "Save"}
                        </button>
                        <button 
                          onClick={cancelEditing} 
                          className="cancel-button"
                          disabled={loading}
                        >
                          Cancel
                        </button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{user.full_name}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`role-badge ${user.role.toLowerCase()}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="action-buttons">
                        <button 
                          onClick={() => startEditing(user)} 
                          className="edit-button"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => requestDeleteUser(user)} 
                          className="delete-button"
                          disabled={user.id === parseInt(localStorage.getItem("user_id"))}
                        >
                          Delete
                        </button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
