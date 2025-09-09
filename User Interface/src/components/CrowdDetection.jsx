import React, { useState } from 'react';

const CrowdDetection = () => {
  const cameras = Array.from({ length: 10 }, (_, i) => ({
    name: `Camera ${i + 1}`,
    percentage: Math.floor(Math.random() * 100) + 1
  }));

  const [selectedCamera, setSelectedCamera] = useState('');
  const [logs, setLogs] = useState([
    { id: 1, camera: 'Camera 1', location: 'North Block', notify: false, resolved: false },
    { id: 2, camera: 'Camera 2', location: 'South Block', notify: true, resolved: false },
    { id: 3, camera: 'Camera 3', location: 'East Wing', notify: false, resolved: true },
    { id: 4, camera: 'Camera 4', location: 'West Block', notify: true, resolved: false },
    { id: 5, camera: 'Camera 5', location: 'North Block', notify: false, resolved: false },
  ]);

  const toggleNotify = (id) => {
    setLogs(logs.map(log => log.id === id ? { ...log, notify: !log.notify } : log));
  };

  const resolve = (id) => {
    setLogs(logs.map(log => log.id === id ? { ...log, resolved: true } : log));
  };

  const getColor = (percentage) => {
    if (percentage > 90) return 'red';
    if (percentage > 70) return 'orange';
    return 'green';
  };

  return (
    <div className="crowd-layout">
      <div className="crowd-section">
        <div className="crowd-card">
          <label className="select-label">Cameras:</label>
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="crowd-select"
          >
            <option value="">Select a Camera</option>
            {cameras.map((cam, index) => (
              <option
                key={index}
                value={cam.name}
                className={getColor(cam.percentage)}
              >
                {cam.name} - {cam.percentage}%
              </option>
            ))}
          </select>
        </div>

        <div className={`crowd-card live-feed ${selectedCamera ? 'selected' : 'placeholder'}`}>
          {selectedCamera ? (
            <div style={{ textAlign: 'center' }}>
              <div className="live-feed-icon">📹</div>
              <p className="live-feed-text">Live Feed from {selectedCamera}</p>
            </div>
          ) : (
            <p className="live-feed-placeholder-text">Select a Camera to View Live Feed</p>
          )}
        </div>
      </div>

      <div className="crowd-section">
        <div className="crowd-card">
          <h3 className="alerts-log">Alerts Log</h3>
          {logs.map((log) => (
            <div key={log.id} className={`crowd-card alert-item ${log.resolved ? 'resolved' : ''}`}>
              <p className="alert-text">
                Cam – {log.camera} | Location: {log.location}
              </p>
              <div className="alert-controls">
                <button
                  onClick={() => toggleNotify(log.id)}
                  className={`crowd-button ${log.notify ? 'notified' : ''}`}
                >
                  {log.notify ? 'Notified' : 'Notify'}
                </button>
                <button
                  onClick={() => resolve(log.id)}
                  className={`crowd-button ${log.resolved ? 'resolved' : ''}`}
                  disabled={log.resolved}
                >
                  {log.resolved ? 'Resolved' : 'Resolve'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CrowdDetection;
