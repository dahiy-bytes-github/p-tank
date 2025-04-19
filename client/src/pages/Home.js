// src/pages/Home.js
import React, { useState } from "react";
import Register from "./Register";
import Login from "./Login";
import "../styles/Home.css";

const Home = () => {
  const [isSigningUp, setIsSigningUp] = useState(false);

  const toggleForm = () => {
    setIsSigningUp((prev) => !prev);
  };

  return (
    <div className="account-container">
      {isSigningUp ? (
        <div>
          <Register />
          <p className="toggle-text">
            Already have an account?{" "}
            <button onClick={toggleForm} className="toggle-link">
              Login Here
            </button>
          </p>
        </div>
      ) : (
        <div>
          <Login />
          <p className="toggle-text">
            Don't have an account?{" "}
            <button onClick={toggleForm} className="toggle-link">
              Register Here
            </button>
          </p>
        </div>
      )}
    </div>
  );
};

export default Home;
