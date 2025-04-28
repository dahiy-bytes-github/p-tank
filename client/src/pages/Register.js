// src/pages/Register.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { validateEmail } from "../utils";
import "../styles/Register.css";

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [emailError, setEmailError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (name === "email" && value) {
      setEmailError(validateEmail(value) ? "" : "Invalid email format");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setEmailError("");

    if (!validateEmail(formData.email)) {
      setEmailError("Please enter a valid email address");
      return;
    }

    try {
      const response = await fetch("http://localhost:5555/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Registration failed");

      // 👇 Redirect to / and show Login form
      navigate("/", { state: { fromRegister: true } });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      <h2>Register</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            className="input-field"
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={formData.full_name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="input-group">
          <input
            className="input-field"
            type="email"
            name="email"
            placeholder="example@email.com"
            value={formData.email}
            onChange={handleChange}
            onBlur={() => {
              if (formData.email) setEmailError(validateEmail(formData.email) ? "" : "Invalid email format");
            }}
            required
          />
          {emailError && <div className="error-message">{emailError}</div>}
        </div>
        <div className="input-group">
          <input
            className="input-field"
            type="password"
            name="password"
            placeholder="Password (min 8 characters)"
            value={formData.password}
            onChange={handleChange}
            required
            minLength="8"
            title="Password must be at least 8 characters"
          />
        </div>
        <button className="login-button" type="submit">
          Register
        </button>
      </form>
    </div>
  );
};

export default Register;
