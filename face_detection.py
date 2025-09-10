import numpy as np
import face_recognition
import cv2

# ---------------------------
# Step 1: Register Face (only run once or if you want to overwrite)
# ---------------------------
try:
    my_face = np.load("my_face.npy")  # Try loading saved encoding
    print("Face encoding loaded successfully!")
except FileNotFoundError:
    print("No saved encoding found. Registering new face...")
    your_image = face_recognition.load_image_file("image.jpeg")  # your clear front photo
    your_encoding = face_recognition.face_encodings(your_image)[0]
    np.save("my_face.npy", your_encoding)
    my_face = your_encoding
    print("Face registered and saved!")

# ---------------------------
# Step 2: Load Target Image for Recognition
# ---------------------------
frame = cv2.imread("image.jpeg")  # Replace with another image if testing recognition
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Detect faces in target image
face_locations = face_recognition.face_locations(rgb_frame)
face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

# ---------------------------
# Step 3: Compare and Draw Results
# ---------------------------
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # Compare with your stored face
    match = face_recognition.compare_faces([my_face], face_encoding, tolerance=0.5)

    if match[0]:
        name = "Lost Person"
        color = (0, 255, 0)
    else:
        name = "Unknown"
        color = (0, 0, 255)

    # Draw bounding box & label
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

# ---------------------------
# Step 4: Show Output
# ---------------------------
cv2.imshow("Face Recognition", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
