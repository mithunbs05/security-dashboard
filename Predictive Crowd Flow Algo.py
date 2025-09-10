"""
Predictive Crowd Flow Analysis
==============================
This program:
- Captures live video (camera/RTSP/file).
- Detects people using YOLOv8 (Ultralytics).
- Computes crowd flow using Optical Flow (Farneback).
- Predicts next movement by extrapolating vectors.
- Generates both Heatmap (density) + Flow Arrows.
- Adaptive: uses arrows for small crowds, heatmap for large.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import argparse


class CrowdFlowPredictor:
    def __init__(self, source=0, model_path="yolov8n.pt", heatmap_size=(720, 1280)):
        """
        Initialize the Crowd Flow Predictor.
        """
        self.source = source
        self.model = YOLO(model_path)  # YOLOv8 model
        self.heatmap_size = heatmap_size
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception("Error: Cannot open video source")

        # Heatmap storage
        self.heatmap = np.zeros(self.heatmap_size, dtype=np.float32)

        # Previous gray frame for optical flow
        self.prev_gray = None

        # Colors for visualization
        self.arrow_color = (0, 0, 255)  # Red arrows
        self.person_color = (0, 255, 0)  # Green dots
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def detect_people(self, frame):
        """
        Detect people using YOLO.
        Returns list of bounding boxes and centers.
        """
        results = self.model(frame, classes=[0], verbose=False)  # Class 0 = person
        people_centers = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box[:4]
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                people_centers.append((cx, cy))
        return people_centers

    def update_heatmap(self, people_centers):
        """
        Update heatmap with new people positions.
        """
        for (x, y) in people_centers:
            if 0 <= y < self.heatmap_size[0] and 0 <= x < self.heatmap_size[1]:
                self.heatmap[y, x] += 1
        # Smooth heatmap
        self.heatmap = cv2.GaussianBlur(self.heatmap, (35, 35), 0)

    def compute_optical_flow(self, frame_gray):
        """
        Compute optical flow between previous and current frames.
        Returns flow vector field.
        """
        if self.prev_gray is None:
            self.prev_gray = frame_gray
            return None

        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, frame_gray, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        self.prev_gray = frame_gray
        return flow

    def visualize_flow(self, frame, flow, step=20, scale=2.0):
        """
        Draw flow vectors (arrows) on frame.
        """
        h, w = frame.shape[:2]
        for y in range(0, h, step):
            for x in range(0, w, step):
                fx, fy = flow[y, x] * scale
                end_point = (int(x + fx), int(y + fy))
                cv2.arrowedLine(frame, (x, y), end_point,
                                self.arrow_color, 1, tipLength=0.3)
        return frame

    def visualize_heatmap(self, frame):
        """
        Overlay heatmap on the frame.
        """
        norm = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_colored = cv2.applyColorMap(norm.astype(np.uint8), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(frame, 0.6, heatmap_colored, 0.4, 0)
        return overlay

    def run(self):
        """
        Main loop for processing video stream.
        """
        print("Starting Crowd Flow Prediction... Press ESC to exit.")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("End of video or error.")
                break

            # Resize frame for consistency
            frame = cv2.resize(frame, (self.heatmap_size[1], self.heatmap_size[0]))

            # Detect people
            people = self.detect_people(frame)

            # Update heatmap
            self.update_heatmap(people)

            # Optical flow prediction
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = self.compute_optical_flow(gray)

            # Draw detected people
            for (cx, cy) in people:
                cv2.circle(frame, (cx, cy), 5, self.person_color, -1)

            # Adaptive visualization
            if len(people) < 30:
                if flow is not None:
                    frame = self.visualize_flow(frame, flow)
                label = f"Mode: Arrows (small crowd: {len(people)})"
            else:
                frame = self.visualize_heatmap(frame)
                label = f"Mode: Heatmap (large crowd: {len(people)})"

            # Add status text
            cv2.putText(frame, label, (20, 30), self.font, 0.8, (255, 255, 255), 2)

            # Show result
            cv2.imshow("Predictive Crowd Flow", frame)

            # Exit on ESC
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="Predictive Crowd Flow Analysis")
    parser.add_argument("--source", type=str, default="0", help="Video source (0 for webcam, path or RTSP URL)")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLOv8 model path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    predictor = CrowdFlowPredictor(source=source, model_path=args.model)
    predictor.run()
