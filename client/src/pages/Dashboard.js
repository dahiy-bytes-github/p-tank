import { Link } from 'react-router-dom';
import '../styles/Dashboard.css';
import './LatestReadingCard';

function Dashboard() {
  return (
    <div className="dashboard-container">
      <p>Manage your septic tank monitoring</p>

      <div className="dashboard-buttons">
        <Link to="/login">
          <button className="dashboard-button">Login</button>
        </Link>
        <Link to="/register">
          <button className="dashboard-button">Register</button>
        </Link>
        <Link to="/logout">
          <button className="dashboard-button">Logout</button>
        </Link>
        <Link to="/latestreading">
          <button className="dashboard-button">LatestReadingCard</button>
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;
