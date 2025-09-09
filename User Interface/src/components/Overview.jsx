import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
const Overview = () => {
  const navigate = useNavigate();
  // Mock data for demonstration; in a real app, this would come from APIs or state
  const [metrics, setMetrics] = useState({
    alerts: 5,
    trafficStatus: 'Normal',
    lostPersons: 2,
    crowdAlerts: 1,
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        alerts: Math.floor(Math.random() * 10),
        lostPersons: Math.floor(Math.random() * 5),
      }));
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleNavigate = (component) => {
    // Placeholder for navigation; in a real app, use React Router or similar
    navigate(`/${component.toLowerCase()}`);
  };

  return (
    <div className="overview-container">
      <h2>Security Dashboard Overview</h2>
      <div className="summary-cards">
        <div className="card">
          <h3>Active Alerts</h3>
          <p className="metric">{metrics.alerts}</p>
          <button onClick={() => handleNavigate('alerts')}>View Details</button>
        </div>
        <div className="card">
          <h3>Traffic Control</h3>
          <p className="metric">{metrics.trafficStatus}</p>
          <button onClick={() => handleNavigate('traffic-control')}>Manage</button>
        </div>
        <div className="card">
          <h3>Lost Persons</h3>
          <p className="metric">{metrics.lostPersons}</p>
          <button onClick={() => handleNavigate('lost-persons')}>View Reports</button>
        </div>
        <div className="card">
          <h3>Crowd Detection</h3>
          <p className="metric">{metrics.crowdAlerts}</p>
          <button onClick={() => handleNavigate('crowd-detection')}>Monitor</button>
        </div>
      </div>
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <button onClick={() => handleNavigate('department')}>Department Overview</button>
        <button onClick={() => handleNavigate('login')}>Login Management</button>
      </div>
    </div>
  );
};

export default Overview;
