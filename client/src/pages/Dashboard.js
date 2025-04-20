// Dashboard.js
import React, { useState, useContext } from "react"; // Added useContext import
import { AuthContext } from "../context/AuthContext";
import "../styles/Dashboard.css";
import SensorReadingsDashboard from "./SensorReadingsDashboard"; // Use consistent naming

const Dashboard = () => {
  const [activeView, setActiveView] = useState('sensorReadings'); // Default view
  const { user } = useContext(AuthContext); // Now properly imported

  // Navigation functions
  const showSensorReadings = () => setActiveView('sensorReadings');
  // Add more show functions for other views as needed

  return (
    <div className="dashboard">
      <h1>Welcome to Your Dashboard, {user?.email}!</h1>
      
      {/* Navigation Menu */}
      <nav className="dashboard-nav">
        <button 
          onClick={showSensorReadings}
          className={activeView === 'sensorReadings' ? 'active' : ''}
        >
          Sensor Readings
        </button>
        {/* Add more navigation buttons for other views */}
      </nav>
      
      {/* Content Area */}
      <div className="dashboard-content">
        {activeView === 'sensorReadings' && <SensorReadingsDashboard />}
        {/* Add more views here as needed */}
      </div>
    </div>
  );
};

export default Dashboard;