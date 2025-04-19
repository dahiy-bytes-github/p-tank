// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Logout from './pages/Logout';
import UserManagement from './pages/UserManagement';
import Navbar from './components/Navbar';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/usermanagement" element={<UserManagement />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
