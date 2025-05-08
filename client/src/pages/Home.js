// src/pages/Home.js
import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import Register from "./Register";
import Login from "./Login";
import "../styles/Home.css";

const Home = () => {
  const [isSigningUp, setIsSigningUp] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (location.state?.fromRegister) {
      setIsSigningUp(false); //Show login after registration
    }
  }, [location.state]);

  const toggleForm = () => {
    setIsSigningUp((prev) => !prev);
  };

  return (
    <div className="home-container">
      <div className="welcome-section">
        <h1 className="welcome-title">Welcome to Predictive Septic Tank Monitoring System</h1>
        <p className="welcome-text">
          The system helps you monitor and predict tank levels.
          Please login to access all features.
        </p>
        <div className="divider"></div>
      </div>

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
    </div>
  );
};

export default Home;
