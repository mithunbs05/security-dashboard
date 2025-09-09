import { BrowserRouter as Router, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Overview from './components/Overview';
import CrowdDetection from './components/CrowdDetection';
import TrafficControl from './components/TrafficControl';
import LostPersons from './components/LostPersons';
import Alerts from './components/Alerts';
import Department from './components/Department';
import { ToastContainer } from 'react-toastify';
import Login from './components/Login';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in (from localStorage or session)
    const loggedIn = localStorage.getItem('isAuthenticated') === 'true';
    setIsAuthenticated(loggedIn);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated');
  };

  if (!isAuthenticated) {
    return (
      <Router>
        <div className="login-page">
          <Login onLogin={handleLogin} />
        </div>
        <ToastContainer />
      </Router>
    );
  }

  return (
    <Router>
      <div className="app-container">
        {/* Header */}
        <header className="header">
          <h1>Surveillance & Safety Dashboard</h1>
        </header>

        {/* Sidebar + Content Wrapper */}
        <div className="content-wrapper">
          {/* Sidebar */}
          <aside className="sidebar">
            <ul>
              <li>
                <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
                  Overview
                </NavLink>
              </li>
              <li>
                <NavLink to="/crowd-detection" className={({ isActive }) => (isActive ? 'active' : '')}>
                  Crowd Detection
                </NavLink>
              </li>
              <li>
                <NavLink to="/traffic-control" className={({ isActive }) => (isActive ? 'active' : '')}>
                  Traffic Control
                </NavLink>
              </li>
              <li>
                <NavLink to="/lost-persons" className={({ isActive }) => (isActive ? 'active' : '')}>
                  Lost Persons
                </NavLink>
              </li>
              <li>
                <NavLink to="/alerts" className={({ isActive }) => (isActive ? 'active' : '')}>
                  Alerts
                </NavLink>
              </li>
              <li>
                <NavLink to="/department" className={({ isActive }) => (isActive ? 'active' : '')}>
                  Department
                </NavLink>
              </li>
              <li className="logout-item">
                <button onClick={handleLogout} className="logout-btn">Logout</button>
              </li>
            </ul>
          </aside>

          {/* Main Content */}
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/crowd-detection" element={<CrowdDetection />} />
              <Route path="/traffic-control" element={<TrafficControl />} />
              <Route path="/lost-persons" element={<LostPersons />} />
              <Route path="/alerts" element={<Alerts /> } />
              <Route path="/department" element={<Department />} />
            </Routes>
          </main>
        </div>
        <ToastContainer />
      </div>
    </Router>
  );
};

export default App;
