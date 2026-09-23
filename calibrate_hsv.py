import cv2
import numpy as np
import json
import os

CONFIG_FILE = "hsv_config.json"

# Default HSV values for 6 colors
hsv_ranges = {
    'red':    {'lower': [0, 100, 100], 'upper': [10, 255, 255]},
    'orange': {'lower': [11, 100, 100], 'upper': [25, 255, 255]},
    'yellow': {'lower': [26, 100, 100], 'upper': [35, 255, 255]}, # Used for some tuning if needed
    'green':  {'lower': [36, 100, 100], 'upper': [85, 255, 255]},
    'cyan':   {'lower': [86, 100, 100], 'upper': [105, 255, 255]},
    'blue':   {'lower': [106, 100, 100], 'upper': [135, 255, 255]},
    'purple': {'lower': [136, 100, 100], 'upper': [170, 255, 255]}
}

def load_config():
    global hsv_ranges
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            hsv_ranges = json.load(f)
            print(f"Loaded config from {CONFIG_FILE}")

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(hsv_ranges, f, indent=4)
    print(f"Saved config to {CONFIG_FILE}")

def nothing(x):
    pass

def main():
    load_config()
    cap = cv2.VideoCapture(0) # Change to 1 if using external webcam
    
    cv2.namedWindow('Calibration')
    
    colors = list(hsv_ranges.keys())
    current_color_idx = 0
    current_color = colors[current_color_idx]
    
    cv2.createTrackbar('H_MIN', 'Calibration', 0, 179, nothing)
    cv2.createTrackbar('S_MIN', 'Calibration', 0, 255, nothing)
    cv2.createTrackbar('V_MIN', 'Calibration', 0, 255, nothing)
    cv2.createTrackbar('H_MAX', 'Calibration', 179, 179, nothing)
    cv2.createTrackbar('S_MAX', 'Calibration', 255, 255, nothing)
    cv2.createTrackbar('V_MAX', 'Calibration', 255, 255, nothing)

    def update_trackbars(color):
        cv2.setTrackbarPos('H_MIN', 'Calibration', hsv_ranges[color]['lower'][0])
        cv2.setTrackbarPos('S_MIN', 'Calibration', hsv_ranges[color]['lower'][1])
        cv2.setTrackbarPos('V_MIN', 'Calibration', hsv_ranges[color]['lower'][2])
        cv2.setTrackbarPos('H_MAX', 'Calibration', hsv_ranges[color]['upper'][0])
        cv2.setTrackbarPos('S_MAX', 'Calibration', hsv_ranges[color]['upper'][1])
        cv2.setTrackbarPos('V_MAX', 'Calibration', hsv_ranges[color]['upper'][2])

    update_trackbars(current_color)

    print("=== HSV Calibration Tool ===")
    print("Press 'n' to switch to NEXT color")
    print("Press 's' to SAVE config")
    print("Press 'q' to QUIT")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Get values from trackbars
        h_min = cv2.getTrackbarPos('H_MIN', 'Calibration')
        s_min = cv2.getTrackbarPos('S_MIN', 'Calibration')
        v_min = cv2.getTrackbarPos('V_MIN', 'Calibration')
        h_max = cv2.getTrackbarPos('H_MAX', 'Calibration')
        s_max = cv2.getTrackbarPos('S_MAX', 'Calibration')
        v_max = cv2.getTrackbarPos('V_MAX', 'Calibration')

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        
        # Update current color dict
        hsv_ranges[current_color]['lower'] = [h_min, s_min, v_min]
        hsv_ranges[current_color]['upper'] = [h_max, s_max, v_max]

        mask = cv2.inRange(hsv, lower, upper)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        # Display text info
        cv2.putText(frame, f"Tuning: {current_color.upper()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'n' next, 's' save, 'q' quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow('Original', frame)
        cv2.imshow('Mask', mask)
        cv2.imshow('Result', res)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            save_config()
        elif key == ord('n'):
            current_color_idx = (current_color_idx + 1) % len(colors)
            current_color = colors[current_color_idx]
            update_trackbars(current_color)
            print(f"Switched to tuning: {current_color}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
