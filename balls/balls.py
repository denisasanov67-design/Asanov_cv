import cv2
import numpy as np
from pathlib import Path
import json
import random

save_path = Path(__file__).parent
config_path = save_path / "config.json"

colors = ["green", "orange", "blue"]
random_order = colors.copy()
random.shuffle(random_order)

print("СЛУЧАЙНЫЙ ПОРЯДОК:", random_order)

cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)

position = [0, 0]
clicked = False

def on_click(event, x, y, flags, params):
    global position, clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        position = [x, y]
        clicked = True

cv2.setMouseCallback("Image", on_click)

cam = cv2.VideoCapture(0)

color_ranges = {}
captured_sequence = []
detected_order = []

current_index = 0

while cam.isOpened():
    ret, frame = cam.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    
    if current_index < len(random_order):
        target_color = random_order[current_index]

        cv2.putText(frame, f"Click on: {target_color}", (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        if clicked:
            clicked = False

            pixel = hsv[position[1], position[0]]

            lower = np.clip(pixel * 0.9, 0, 255).astype("u1")
            upper = np.clip(pixel * 1.1, 0, 255).astype("u1")
            upper[1] = 255
            upper[2] = 255

            color_ranges[target_color] = {
                "lower": lower.tolist(),
                "upper": upper.tolist()
            }

            captured_sequence.append(target_color)

            print(f"Откалиброван и считан: {target_color}")

            current_index += 1

    else:
        centers = []

        for color_name in colors:
            if color_name not in color_ranges:
                continue

            cr = color_ranges[color_name]
            lower = np.array(cr["lower"], dtype=np.uint8)
            upper = np.array(cr["upper"], dtype=np.uint8)

            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), dtype="u1"))

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                contour = max(contours, key=cv2.contourArea)
                (x,y), radius = cv2.minEnclosingCircle(contour)

                if radius > 10:
                    x, y = int(x), int(y)
                    centers.append((x, y, color_name))

                    cv2.circle(frame, (x, y), int(radius), (0,255,255), 2)
                    cv2.putText(frame, color_name, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        if len(centers) == len(colors):
            centers.sort(key=lambda c: c[0])
            detected_order = [c[2] for c in centers]

            cv2.putText(frame, f"{detected_order}", (20,80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)


            if detected_order == random_order:
                result = "MATCH"
            else:
                result = "NO MATCH"

            cv2.putText(frame, result, (20,120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    cv2.imshow("Image", frame)

cam.release()
cv2.destroyAllWindows()


with config_path.open("w") as f:
    json.dump({
        "random_order": random_order,
        "captured_sequence": captured_sequence,
        "detected_order": detected_order
    }, f, indent=4)