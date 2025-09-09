import React, { useState } from 'react';

const TrafficControl = () => {
  const cameras = [
    { id: 1, name: 'Cam – Entrance 1', location: 'North Gate' },
    { id: 2, name: 'Cam – Entrance 2', location: 'East Gate' },
    { id: 3, name: 'Cam – Entrance 3', location: 'South Gate' },
    { id: 4, name: 'Cam – Out Gate 1', location: 'West Gate' },
    { id: 5, name: 'Cam – Out Gate 2', location: 'Main Gate' },
  ];

  const [alerts, setAlerts] = useState([
    { id: 1, camera: 'Cam – Entrance 2', location: 'North Gate', message: 'Overcapacity detected', notify: false, resolved: false },
    { id: 2, camera: 'Cam – Entrance 3', location: 'East Gate', message: 'Toll Closed', notify: true, resolved: false },
    { id: 3, camera: 'Cam – Out Gate 1', location: 'South Gate', message: 'Accident reported', notify: false, resolved: true },
  ]);

  const [stats] = useState({
    vehicleInTotal: 5000,
    vehicleOutTotal: 3000,
    totalFreeSpace: 50,
    tollGateStatus: 'Open',
    currentlyParked: 2000,
  });

  const toggleNotify = (id) => {
    setAlerts(alerts.map(alert => alert.id === id ? { ...alert, notify: !alert.notify } : alert));
  };

  const resolveAlert = (id) => {
    setAlerts(alerts.map(alert => alert.id === id ? { ...alert, resolved: true } : alert));
  };

  return (
    <div className="traffic-layout">
      <div className="traffic-left">
        <div className="traffic-cameras">
          <h3>Camera Section</h3>
          <ul>
            {cameras.map(cam => (
              <li key={cam.id}>
                <strong>{cam.name}</strong><br />
                <small>{cam.location}</small>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="traffic-right">
        <div className="traffic-stats">
          <h3>Vehicle Statistics</h3>
          <div className="stats-card">
            <div className="stat-item">
              <span className="stat-label">Vehicle In Total:</span>
              <span className="stat-value">{stats.vehicleInTotal}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Vehicle Out Total:</span>
              <span className="stat-value">{stats.vehicleOutTotal}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Free Space:</span>
              <span className="stat-value">{stats.totalFreeSpace}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Toll Gate Status:</span>
              <span className="stat-value">{stats.tollGateStatus}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Currently Parked:</span>
              <span className="stat-value">{stats.currentlyParked}</span>
            </div>
          </div>
        </div>

        <div className="traffic-alerts">
          <h3>Alerts Section</h3>
          {alerts.map(alert => (
            <div key={alert.id} className={`alert-card ${alert.resolved ? 'resolved' : ''}`}>
              <p><strong>{alert.camera}</strong> | Location: {alert.location}</p>
              <p>{alert.message}</p>
              <div className="alert-actions">
                <button
                  onClick={() => toggleNotify(alert.id)}
                  className={`traffic-button ${alert.notify ? 'notified' : ''}`}
                >
                  {alert.notify ? 'Notified' : 'Notify'}
                </button>
                <button
                  onClick={() => resolveAlert(alert.id)}
                  className={`traffic-button ${alert.resolved ? 'resolved' : ''}`}
                  disabled={alert.resolved}
                >
                  {alert.resolved ? 'Resolved' : 'Resolve'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrafficControl;
