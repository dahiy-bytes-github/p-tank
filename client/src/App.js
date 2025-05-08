// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Logout from './pages/Logout';
import UserManagement from './pages/UserManagement';
import NotificationList from './pages/NotificationList';
import UserSettings from './pages/UserSettings';
import Navbar from './components/Navbar';
import { AuthProvider } from './context/AuthContext';
import PredictionCard from './pages/PredictionCard';
import GetAllUsersNotifications from './pages/GetAllUsersNotifications';
import './styles/App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        {/* Add a div here to offset the fixed navbar */}
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard/*" element={<Dashboard />} />
            <Route path="/notifications" element={<NotificationList />} />
            <Route path="/settings" element={<UserSettings />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/usermanagement" element={<UserManagement />} />
            <Route path="/prediction" element={<PredictionCard />} />
            <Route path="/allusersnotifications" element={<GetAllUsersNotifications />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
