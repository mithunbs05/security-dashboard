import cv2
import numpy as np
from ultralytics import YOLO
import os
import datetime
import csv
import time

# --- Video and Display Configuration ---
VIDEO_FILE_PATH = r"C:\Users\Administrator\Downloads\DJI_0887.MP4"
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# --- Snapshot and logging settings ---
SNAPSHOT_IN_DIR = "snapshots_in2"
SNAPSHOT_OUT_DIR = "snapshots_out2"
CSV_IN_FILE = "vehicle_log_in2.csv"
CSV_OUT_FILE = "vehicle_log_out2.csv"

# Create snapshot directories if they don't exist
os.makedirs(SNAPSHOT_IN_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_OUT_DIR, exist_ok=True)

# COCO class names for vehicles
# Class IDs: 2: car, 3: motorcycle, 5: bus, 7: truck
CLASS_NAMES = {
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

# --- Helper Functions ---

# Line intersection function
def intersect(A, B, C, D):
    """Check if line segments AB and CD intersect."""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

# Function to initialize CSV files with headers
def initialize_csv():
    """Creates the CSV files and writes the headers if the files don't exist."""
    for csv_file in [CSV_IN_FILE, CSV_OUT_FILE]:
        if not os.path.exists(csv_file):
            with open(csv_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'vehicle_id', 'vehicle_type', 'image_path', 'direction'])

# Function to log data to CSV
def log_to_csv(timestamp, vehicle_id, vehicle_type, image_path, direction):
    """Appends a new row of data to the appropriate CSV file."""
    csv_file = CSV_IN_FILE if direction == "in" else CSV_OUT_FILE
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, vehicle_id, vehicle_type, image_path, direction])

# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
# NEW FUNCTION: To draw a prominent, large display for vehicle counts
# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

def draw_dashboard(frame, in_counts, out_counts):
    """
    Draws a semi-transparent dashboard on the frame with large text for vehicle counts.
    This version dynamically aligns text to prevent overlapping.
    """
    # --- Dashboard Configuration ---
    # You can easily change these values to customize the look
    PANEL_START_X = 20
    PANEL_START_Y = 20
    PANEL_BG_COLOR = (0, 0, 0)      # Black background
    PANEL_ALPHA = 0.5              # Transparency
    HEADER_FONT_SCALE = 1.5
    DATA_FONT_SCALE = 1.2
    FONT_THICKNESS = 2
    FONT_FACE = cv2.FONT_HERSHEY_TRIPLEX
    TEXT_COLOR_WHITE = (255, 255, 255)
    TEXT_COLOR_IN = (255, 200, 100) # Light Blue
    TEXT_COLOR_OUT = (100, 100, 255) # Light Red
    
    # --- Layout Configuration ---
    # Increased column width to ensure enough space for all text
    COL_WIDTH = 350
    # Horizontal and vertical spacing for text
    H_PADDING = 40
    LINE_HEIGHT = 50

    # --- Create the semi-transparent background ---
    overlay = frame.copy()
    # Determine the required height of the panel
    num_vehicle_types = max(len(in_counts), len(out_counts))
    panel_height = (num_vehicle_types + 2) * LINE_HEIGHT # +2 for header and padding
    panel_width = (2 * COL_WIDTH) + H_PADDING # Two columns + padding
    
    cv2.rectangle(overlay, 
                  (PANEL_START_X, PANEL_START_Y), 
                  (PANEL_START_X + panel_width, PANEL_START_Y + panel_height), 
                  PANEL_BG_COLOR, 
                  -1) # Filled rectangle
                  
    # Blend the overlay with the original frame
    cv2.addWeighted(overlay, PANEL_ALPHA, frame, 1 - PANEL_ALPHA, 0, frame)

    # --- Draw the Text ---
    # Column 1: INBOUND
    in_col_x = PANEL_START_X + H_PADDING
    current_y = PANEL_START_Y + LINE_HEIGHT
    cv2.putText(frame, "INBOUND", (in_col_x, current_y), FONT_FACE, HEADER_FONT_SCALE, TEXT_COLOR_IN, FONT_THICKNESS + 1)
    
    for v_type, count in in_counts.items():
        current_y += LINE_HEIGHT
        text = f"{v_type.title()}: {count}"
        cv2.putText(frame, text, (in_col_x + 20, current_y), FONT_FACE, DATA_FONT_SCALE, TEXT_COLOR_WHITE, FONT_THICKNESS)
        
    # Column 2: OUTBOUND
    out_col_x = in_col_x + COL_WIDTH
    current_y = PANEL_START_Y + LINE_HEIGHT # Reset Y for the new column
    cv2.putText(frame, "OUTBOUND", (out_col_x, current_y), FONT_FACE, HEADER_FONT_SCALE, TEXT_COLOR_OUT, FONT_THICKNESS + 1)
    
    for v_type, count in out_counts.items():
        current_y += LINE_HEIGHT
        text = f"{v_type.title()}: {count}"
        cv2.putText(frame, text, (out_col_x + 20, current_y), FONT_FACE, DATA_FONT_SCALE, TEXT_COLOR_WHITE, FONT_THICKNESS)
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# END OF NEW, MODIFIED FUNCTION
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# END OF NEW FUNCTION
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# --- Main Application ---
def main():
    # Initialize YOLO model
    model = YOLO("yolo11m-seg.pt")

    # Open the video file
    cap = cv2.VideoCapture(VIDEO_FILE_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {VIDEO_FILE_PATH}")
        return

    # Get video properties
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get the first frame for ROI setup
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Could not read the first frame of the video.")
        cap.release()
        return

    # Calculate resize ratio for display
    resize_ratio = min(DISPLAY_WIDTH / W, DISPLAY_HEIGHT / H)
    display_dims = (int(W * resize_ratio), int(H * resize_ratio))

    # --- ROI and Line Drawing ---
    roi_points = []
    in_line = []  # Blue line for incoming vehicles
    out_line = []  # Red line for outgoing vehicles

    def draw_roi(event, x, y, flags, param):
        """Mouse callback function to draw ROI and counting lines."""
        nonlocal roi_points, in_line, out_line
        original_x = int(x / resize_ratio)
        original_y = int(y / resize_ratio)
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(roi_points) < 4:
                roi_points.append((original_x, original_y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(in_line) < 2:
                in_line.append((original_x, original_y))
        elif event == cv2.EVENT_MBUTTONDOWN:
            if len(out_line) < 2:
                out_line.append((original_x, original_y))

    cv2.namedWindow("Draw ROI and Counting Lines")
    cv2.setMouseCallback("Draw ROI and Counting Lines", draw_roi)
    instructions = [
        "Left click to add ROI points (up to 4 for polygon)",
        "Right click to set IN counting line (blue, 2 points)",
        "Middle click to set OUT counting line (red, 2 points)",
        "Press 'c' to clear drawings",
        "Press 'q' when done to start tracking"
    ]

    while True:
        display_frame = first_frame.copy()
        display_frame = cv2.resize(display_frame, display_dims)
        for i, text in enumerate(instructions):
            cv2.putText(display_frame, text, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if roi_points:
            scaled_roi_points = np.array([(int(p[0] * resize_ratio), int(p[1] * resize_ratio)) for p in roi_points], np.int32)
            for point in scaled_roi_points:
                cv2.circle(display_frame, tuple(point), 5, (0, 255, 0), -1)
            cv2.polylines(display_frame, [scaled_roi_points], isClosed=(len(roi_points) == 4), color=(0, 255, 0), thickness=2)
        if in_line:
            scaled_in_line = [(int(p[0] * resize_ratio), int(p[1] * resize_ratio)) for p in in_line]
            for point in scaled_in_line:
                cv2.circle(display_frame, point, 5, (255, 0, 0), -1)
            if len(in_line) == 2:
                cv2.line(display_frame, scaled_in_line[0], scaled_in_line[1], (255, 0, 0), 2)
        if out_line:
            scaled_out_line = [(int(p[0] * resize_ratio), int(p[1] * resize_ratio)) for p in out_line]
            for point in scaled_out_line:
                cv2.circle(display_frame, point, 5, (0, 0, 255), -1)
            if len(out_line) == 2:
                cv2.line(display_frame, scaled_out_line[0], scaled_out_line[1], (0, 0, 255), 2)
        cv2.imshow("Draw ROI and Counting Lines", display_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('c'): roi_points, in_line, out_line = [], [], []

    cv2.destroyAllWindows()

    if len(roi_points) < 3 or len(in_line) != 2 or len(out_line) != 2:
        print("Error: Please define a valid ROI (3+ points), IN line (2 points), and OUT line (2 points).")
        cap.release()
        return

    roi_polygon = np.array(roi_points, np.int32)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # --- Tracking and Counting ---
    initialize_csv()
    track_history = {}
    in_counts = {name: 0 for name in CLASS_NAMES.values()}
    out_counts = {name: 0 for name in CLASS_NAMES.values()}
    
    crossed_ids = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video file.")
            break
            
        original_frame = frame.copy()

        results = model.track(
            frame, persist=True, tracker="custom_tracker.yaml", device="cuda",
            classes=list(CLASS_NAMES.keys()), verbose=False, conf = 0.5
        )
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            
            for box, track_id, cls in zip(boxes, track_ids, clss):
                x, y, w, h = box
                center = (int(x), int(y))
                
                if cv2.pointPolygonTest(roi_polygon, center, False) >= 0:
                    track_history.setdefault(track_id, []).append(center)
                    if len(track_history[track_id]) > 30:
                        track_history[track_id].pop(0)
                    
                    if len(track_history[track_id]) > 1:
                        points = np.array(track_history[track_id], np.int32).reshape((-1, 1, 2))
                        cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 255), thickness=2)
                    
                    if track_id not in crossed_ids:
                        if len(track_history[track_id]) < 2:
                            continue

                        prev_point = track_history[track_id][-2]
                        current_point = track_history[track_id][-1]
                        direction = None
                        
                        if intersect(in_line[0], in_line[1], prev_point, current_point):
                            direction = "in"
                        elif intersect(out_line[0], out_line[1], prev_point, current_point):
                            direction = "out"
                        
                        if direction:
                            crossed_ids.add(track_id)
                            vehicle_type = CLASS_NAMES.get(cls, 'unknown')
                            
                            if direction == "in":
                                in_counts[vehicle_type] += 1
                            else:
                                out_counts[vehicle_type] += 1
                            
                            timestamp = datetime.datetime.now()
                            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
                            x1, y1 = max(0, int(x - w / 2)), max(0, int(y - h / 2))
                            x2, y2 = min(W, int(x + w / 2)), min(H, int(y + h / 2))
                            snapshot = original_frame[y1:y2, x1:x2]
                            
                            dir_path = SNAPSHOT_IN_DIR if direction == "in" else SNAPSHOT_OUT_DIR
                            image_filename = f"{timestamp_str}{vehicle_type}{track_id}.jpg"
                            image_path = os.path.join(dir_path, image_filename)
                            
                            if snapshot.size > 0:
                                cv2.imwrite(image_path, snapshot)
                            else:
                                image_path = "N/A (empty crop)"
                            
                            log_to_csv(timestamp.strftime("%Y-%m-%d %H:%M:%S"), track_id, vehicle_type, image_path, direction)

        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        # MODIFIED DRAWING SECTION
        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        
        # --- Drawing on Frame for Display ---
        # Draw the ROI and counting lines
        cv2.polylines(frame, [roi_polygon], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.line(frame, in_line[0], in_line[1], (255, 0, 0), 2)  # IN line (Blue)
        cv2.line(frame, out_line[0], out_line[1], (0, 0, 255), 2) # OUT line (Red)

        # Draw the new, large dashboard for counts
        draw_dashboard(frame, in_counts, out_counts)

        # --- Display the final frame ---
        display_frame = cv2.resize(frame, display_dims)
        cv2.imshow("Vehicle Tracking (IN: Blue, OUT: Red)", display_frame)
        
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        # END OF MODIFIED DRAWING SECTION
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        
        if cv2.waitKey(1) == 27:  # Press ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()