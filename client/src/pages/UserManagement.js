import React, { useContext, useEffect, useState, useCallback } from "react";
import { AuthContext } from "../context/AuthContext";
import '../styles/UserManagement.css'; // Import the CSS file for styling

const UserManagement = () => {
  const { user } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [editingUserId, setEditingUserId] = useState(null);
  const [editedUser, setEditedUser] = useState({
    full_name: "",
    email: "",
    role: "User",
  });

  const accessToken = localStorage.getItem("access_token");

  // Memoized fetchUsers function to avoid re-creating it on every render
  const fetchUsers = useCallback(async () => {
    console.log("🔄 Fetching users...");
    try {
      const response = await fetch("http://localhost:5555/users", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Error fetching users:", data);
        return;
      }

      console.log("✅ Users fetched:", data);
      setUsers(data.users || []);
    } catch (error) {
      console.error("❌ Network error:", error);
    }
  }, [accessToken]); // useCallback ensures the function is only recreated if accessToken changes

  // If no user or not admin, don't fetch users
  useEffect(() => {
    if (user?.role === "Admin") {
      fetchUsers();
    }
  }, [user, fetchUsers]); // Added fetchUsers to the dependency array

  const startEditing = (user) => {
    setEditingUserId(user.id);
    setEditedUser({
      full_name: user.full_name,
      email: user.email,
      role: user.role,
    });
  };

  const cancelEditing = () => {
    setEditingUserId(null);
    setEditedUser({
      full_name: "",
      email: "",
      role: "User",
    });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditedUser((prev) => ({ ...prev, [name]: value }));
  };

  const saveEdit = async (id) => {
    console.log(`💾 Saving edit for user ${id}...`, editedUser);
    try {
      const response = await fetch(`http://localhost:5555/users/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(editedUser),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Edit failed:", data);
        return;
      }

      console.log("✅ Edit successful:", data);
      fetchUsers();
      cancelEditing();
    } catch (error) {
      console.error("❌ Error saving user:", error);
    }
  };

  const deleteUser = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      const response = await fetch(`http://localhost:5555/users/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Delete failed:", data);
        return;
      }

      console.log("🗑️ User deleted:", data);
      fetchUsers();
    } catch (error) {
      console.error("❌ Error deleting user:", error);
    }
  };

  if (!user) {
    return <p>🔒 Please log in to manage users.</p>;
  }

  if (user.role !== "Admin") {
    return <p>🚫 You do not have permission to access this page.</p>;
  }

  return (
    <div className="UserManagement">
      <h1>User Management</h1>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Full Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) =>
              editingUserId === user.id ? (
                <tr key={user.id}>
                  <td>
                    <input
                      type="text"
                      name="full_name"
                      value={editedUser.full_name}
                      onChange={handleEditChange}
                    />
                  </td>
                  <td>
                    <input
                      type="email"
                      name="email"
                      value={editedUser.email}
                      onChange={handleEditChange}
                    />
                  </td>
                  <td>
                    <select
                      name="role"
                      value={editedUser.role}
                      onChange={handleEditChange}
                    >
                      <option value="Admin">Admin</option>
                      <option value="Normal">Normal</option>
                    </select>
                  </td>
                  <td>
                    <button className="save-button" onClick={() => saveEdit(user.id)}>Save</button>
                    <button className="cancel-button" onClick={cancelEditing}>Cancel</button>
                  </td>
                </tr>
              ) : (
                <tr key={user.id}>
                  <td>{user.full_name}</td>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>
                    <button onClick={() => startEditing(user)}>Edit</button>
                    <button onClick={() => deleteUser(user.id)}>Delete</button>
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default UserManagement;