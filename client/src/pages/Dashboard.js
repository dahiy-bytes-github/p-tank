import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import SensorReadingsDashboard from "./SensorReadingsDashboard";
import "../styles/Dashboard.css";

const Dashboard = () => {
  const { user } = useContext(AuthContext);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome, {user?.full_name || 'User'}!</h1>
        <p className="welcome-message">
          Here's your septic tank monitoring dashboard
        </p>
      </div>
      
      {/* Directly display the sensor readings content */}
      <div className="dashboard-content">
        <SensorReadingsDashboard />
      </div>
    </div>
  );
};

export default Dashboard;