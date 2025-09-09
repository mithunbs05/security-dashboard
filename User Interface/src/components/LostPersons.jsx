import React, { useState } from 'react';
import resultImage from '../assets/image1.jpg'; // ✅ adjust path if needed

const LostPersons = () => {
  const [image, setImage] = useState(null);
  const [camNumber, setCamNumber] = useState(null);

  const generateRandomCam = () => {
    // generates a random number between 1 and 10
    return Math.floor(Math.random() * 10) + 1;
  };

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(URL.createObjectURL(e.target.files[0]));
      setCamNumber(generateRandomCam());
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setImage(URL.createObjectURL(e.dataTransfer.files[0]));
      setCamNumber(generateRandomCam());
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="upload-detection-layout">
      <div className="upload-section">
        <div className="upload-card">
          <h3>Upload Image</h3>
          <div
            className="upload-dropzone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {image ? (
              <img src={image} alt="Uploaded" className="upload-preview" />
            ) : (
              <div className="upload-placeholder">
                <span className="upload-icon">☁️⬆️</span>
                <p>Drag and drop an image here or</p>
                <label htmlFor="file-upload" className="upload-button">
                  Upload
                </label>
                <input
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  style={{ display: 'none' }}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="detection-section">
        <div className="detection-card">
          <h3>Result / Detection</h3>
          {image ? (
            <div className="detection-result">
              {/* ✅ Always show fixed image from assets */}
              <img src={resultImage} alt="Detection" className="detection-image" />
              <p className="detection-summary">
                Cam {camNumber} Detected
              </p>
            </div>
          ) : (
            <p className="detection-placeholder">
              Detection results will appear here
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default LostPersons;
