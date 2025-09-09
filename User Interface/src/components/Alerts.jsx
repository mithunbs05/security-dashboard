import { useState } from "react";
import { toast } from "react-toastify";

const Alerts = () => {
  const alertData = [
    { cam: "Cam 7", message: "Traffic detected" },
    { cam: "Cam 1", message: "Crowd detected" },
    { cam: "Cam 4", message: "Fire detected" },
  ];

  const [reportedStatuses, setReportedStatuses] = useState(new Array(alertData.length).fill(false));

  const handlereport = (index) => {
    setReportedStatuses(prev => {
      const newStatuses = [...prev];
      newStatuses[index] = true;
      return newStatuses;
    });
    toast.success("The report has been sent to all departments");
  };

  return (
    <div className="alerts-container">
      <h2 className="alerts-title">ALERTS</h2>
      <div className="alerts-box">
        {alertData.map((alert, index) => (
          <div key={index} className="alert-item">
            <span className="alert-text">
              {alert.cam} - {alert.message}
            </span>
            <button onClick={() => handlereport(index)} className={`report-btn ${reportedStatuses[index] ? "reported" : ""}`}>
              {reportedStatuses[index] ? "Reported" : "Report"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Alerts;
