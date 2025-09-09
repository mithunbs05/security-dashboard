import cv2
import numpy as np
from collections import deque

# --- Load maze ---
maze_img = cv2.imread("temple.jpg", cv2.IMREAD_GRAYSCALE)
if maze_img is None:
    raise FileNotFoundError("Maze image not found!")

# Convert to binary: 0 = path, 1 = wall
_, maze = cv2.threshold(maze_img, 127, 1, cv2.THRESH_BINARY_INV)

# Optional: Dilate walls to make path more centered
kernel = np.ones((3,3), np.uint8)
maze_dilated = cv2.dilate(maze, kernel, iterations=1)

start_point = None
end_point = None

# --- Function to load fire icon safely ---
def load_fire_icon(path):
    fire = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if fire is None:
        raise FileNotFoundError("Fire icon not found!")

    # If no alpha channel, create one (make black background transparent)
    if fire.shape[2] == 3:
        gray = cv2.cvtColor(fire, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        fire = np.dstack([fire, alpha])
    return fire

# Load fire icon
fire_icon = load_fire_icon("fire.jpg")

# --- Overlay function ---
def overlay_image(bg, overlay, x, y):
    """ Overlay RGBA image onto BGR background at (x,y). """
    h, w = overlay.shape[:2]
    if y+h > bg.shape[0] or x+w > bg.shape[1]:
        return bg  # Skip if out of bounds

    alpha = overlay[:,:,3] / 255.0
    for c in range(3):
        bg[y:y+h, x:x+w, c] = (1 - alpha) * bg[y:y+h, x:x+w, c] + alpha * overlay[:,:,c]
    return bg

# --- Mouse callback ---
def select_points(event, x, y, flags, param):
    global start_point, end_point
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            start_point = (y, x)
            print(f"🔥 Fire detected at: {start_point}")
        elif end_point is None:
            end_point = (y, x)
            print(f"End point: {end_point}")

cv2.namedWindow("Maze")
cv2.setMouseCallback("Maze", select_points)

print("Click start (fire) and end points on the maze.")

while True:
    display_img = cv2.cvtColor(maze_img.copy(), cv2.COLOR_GRAY2BGR)
    if start_point:
        fire_resized = cv2.resize(fire_icon, (60,60))
        display_img = overlay_image(display_img, fire_resized, start_point[1]-15, start_point[0]-15)
    if end_point:
        cv2.circle(display_img, (end_point[1], end_point[0]), 5, (0,0,255), -1)
    cv2.imshow("Maze", display_img)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
    if start_point and end_point:
        break

cv2.destroyAllWindows()

# --- BFS for shortest path ---
def bfs(maze, start, end):
    rows, cols = maze.shape
    visited = np.zeros_like(maze)
    prev = np.full((rows, cols, 2), -1, dtype=int)
    queue = deque([start])
    visited[start] = 1
    directions = [(-1,0),(1,0),(0,-1),(0,1)]  # up, down, left, right

    while queue:
        current = queue.popleft()
        if current == end:
            break
        for dr, dc in directions:
            nr, nc = current[0]+dr, current[1]+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr, nc] == 0 and not visited[nr, nc]:
                queue.append((nr, nc))
                visited[nr, nc] = 1
                prev[nr, nc] = current

    # Reconstruct path
    path = []
    at = end
    while at != (-1,-1):
        path.append(at)
        at = tuple(prev[at])
    path.reverse()

    if path[0] == start:
        return path
    else:
        return None

# --- Find and draw path ---
path = bfs(maze_dilated, start_point, end_point)
if path:
    print(f"Path found! Length: {len(path)}")
    maze_display = cv2.cvtColor(maze_img.copy(), cv2.COLOR_GRAY2BGR)

    # Draw fire at start point
    fire_resized = cv2.resize(fire_icon, (60,60))
    maze_display = overlay_image(maze_display, fire_resized, start_point[1]-15, start_point[0]-15)

    # Draw smooth path
    path_points = np.array([(c,r) for r,c in path], np.int32)
    path_points = path_points.reshape((-1,1,2))
    cv2.polylines(maze_display, [path_points], isClosed=False, color=(0,0,255), thickness=2)

    cv2.imshow("Shortest Path", maze_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No path found!")
