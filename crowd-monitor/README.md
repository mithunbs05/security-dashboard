
# Face Detection, Recognition & Overcrowd Alert System

This project combines:
- **Face Registration & Recognition** → Register one face and detect it in images/videos.
- **Overcrowd Detection** → Count the number of people in a frame and trigger an alert when the count exceeds a set threshold.

---

## 🚀 Features
- Register a single face (`my_face.npy` will be saved for reuse).
- Detect and recognize the registered face in images.
- Detect and count all people present in a frame.
- Trigger **Overcrowd Alert** if the count exceeds your configured limit.
- Works with **static images** and can be extended to **live webcam feed**.

---

## 📦 Dependencies

Make sure you have the following installed:

- Python **3.8+**  
- [OpenCV](https://opencv.org/) → for image & video processing  
- [face_recognition](https://github.com/ageitgey/face_recognition) → for face detection & encoding  
- [dlib](http://dlib.net/) → backend for face recognition (installed automatically with `face_recognition`)  
- NumPy → for saving & loading face encodings
- Deepstream **7.1**
  

### Installation

Note : pyds must be bulided Please Refer Deepstream Documentations 

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install opencv-python face_recognition numpy 

