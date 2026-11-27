
import cv2
import csv
import sys
import time
import numpy as np

from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR))

from database.db_connection import save_crossing_event, save_vehicle


VIDEO_PATH = BASE_DIR / "videos" / "traffic.webm"

OUTPUT_PATH = BASE_DIR / "outputs" / "vehicle_detection.mp4"

CSV_PATH = BASE_DIR / "outputs" / "line_crossing_events.csv"


# --------------------------------------------------
# VEHICLE CLASSES
# --------------------------------------------------

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


# --------------------------------------------------
# DETECTION SETTINGS
# --------------------------------------------------

LINE_POSITION = 0.55

CONFIDENCE = 0.40

FRAME_SIZE = 640


# --------------------------------------------------
# VEHICLE COLOR CLASSIFICATION
# --------------------------------------------------

def classify_vehicle_color(vehicle_crop):

    if vehicle_crop is None or vehicle_crop.size == 0:
        return "Unknown"

    height, width = vehicle_crop.shape[:2]

    if height < 10 or width < 10:
        return "Unknown"

    # Crop central body area
    x1 = int(width * 0.15)
    x2 = int(width * 0.85)

    y1 = int(height * 0.25)
    y2 = int(height * 0.75)

    center_crop = vehicle_crop[y1:y2, x1:x2]

    if center_crop.size == 0:
        return "Unknown"

    center_crop = cv2.resize(center_crop, (100, 100))

    hsv = cv2.cvtColor(center_crop, cv2.COLOR_BGR2HSV)

    masks = {

        "Red": (
            cv2.inRange(
                hsv,
                np.array([0, 80, 50]),
                np.array([10, 255, 255])
            )
            |
            cv2.inRange(
                hsv,
                np.array([170, 80, 50]),
                np.array([180, 255, 255])
            )
        ),

        "Yellow": cv2.inRange(
            hsv,
            np.array([15, 80, 80]),
            np.array([35, 255, 255])
        ),

        "Green": cv2.inRange(
            hsv,
            np.array([36, 50, 40]),
            np.array([85, 255, 255])
        ),

        "Blue": cv2.inRange(
            hsv,
            np.array([90, 60, 40]),
            np.array([135, 255, 255])
        ),

        "White": cv2.inRange(
            hsv,
            np.array([0, 0, 170]),
            np.array([180, 65, 255])
        ),

        "Black": cv2.inRange(
            hsv,
            np.array([0, 0, 0]),
            np.array([180, 255, 55])
        ),

        "Silver/Grey": cv2.inRange(
            hsv,
            np.array([0, 0, 56]),
            np.array([180, 65, 169])
        )
    }

    total_pixels = hsv.shape[0] * hsv.shape[1]

    percentages = {
        name: cv2.countNonZero(mask) / total_pixels * 100
        for name, mask in masks.items()
    }

    best_color = max(percentages, key=percentages.get)

    if percentages[best_color] < 8:
        return "Other"

    return best_color


# --------------------------------------------------
# MAIN DETECTION FUNCTION
# --------------------------------------------------

def run_detection(stop_event, publish_frame, publish_stats):

    print("Loading YOLO model...")

    model = YOLO("yolo11n.pt")

    print("Opening traffic video...")

    cap = cv2.VideoCapture(str(VIDEO_PATH))

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video: {VIDEO_PATH}"
        )

    # Create output directories
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Video properties
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Output video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video_writer = cv2.VideoWriter(
        str(OUTPUT_PATH),
        fourcc,
        fps,
        (frame_width, frame_height)
    )

    # CSV file
    csv_file = open(
        CSV_PATH,
        "w",
        newline="",
        encoding="utf-8"
    )

    csv_writer = csv.writer(csv_file)

    csv_writer.writerow([
        "Vehicle ID",
        "Vehicle Type",
        "Vehicle Color",
        "Direction",
        "Timestamp"
    ])

    # --------------------------------------------------
    # TRACKING DATA
    # --------------------------------------------------

    counted_vehicles = set()

    saved_vehicles = set()

    crossed_vehicles = set()

    previous_positions = {}

    vehicle_colors = {}

    vehicle_counts = {
        "Car": 0,
        "Bus": 0,
        "Truck": 0,
        "Motorcycle": 0
    }

    total_crossings = 0

    total_vehicles = 0

    print("Vehicle detection started!")

    try:

        # --------------------------------------------------
        # VIDEO PROCESSING LOOP
        # --------------------------------------------------

        while not stop_event.is_set():

            ret, frame = cap.read()

            if not ret:
                print("Video processing completed.")
                break

            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=list(VEHICLE_CLASSES.keys()),
                conf=CONFIDENCE,
                imgsz=FRAME_SIZE,
                verbose=False
            )

            annotated_frame = frame.copy()

            line_y = int(frame_height * LINE_POSITION)

            # Draw counting line
            cv2.line(
                annotated_frame,
                (0, line_y),
                (frame_width, line_y),
                (0, 0, 255),
                2
            )

            current_visible = 0

            # --------------------------------------------------
            # PROCESS DETECTIONS
            # --------------------------------------------------

            if results and results[0].boxes is not None:

                boxes = results[0].boxes

                for box in boxes:

                    if box.id is None:
                        continue

                    vehicle_id = int(box.id[0])

                    class_id = int(box.cls[0])

                    vehicle_type = VEHICLE_CLASSES.get(
                        class_id,
                        "Unknown"
                    )

                    if vehicle_type == "Unknown":
                        continue

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist()
                    )

                    # Keep coordinates inside frame
                    x1 = max(0, min(x1, frame_width - 1))
                    x2 = max(0, min(x2, frame_width))
                    y1 = max(0, min(y1, frame_height - 1))
                    y2 = max(0, min(y2, frame_height))

                    if x2 <= x1 or y2 <= y1:
                        continue

                    current_visible += 1

                    center_x = (x1 + x2) // 2

                    center_y = (y1 + y2) // 2

                    # --------------------------------------------------
                    # VEHICLE COLOR
                    # --------------------------------------------------

                    if vehicle_id not in vehicle_colors:

                        vehicle_crop = frame[y1:y2, x1:x2]

                        vehicle_colors[vehicle_id] = (
                            classify_vehicle_color(vehicle_crop)
                        )

                    vehicle_color = vehicle_colors[vehicle_id]

                    # --------------------------------------------------
                    # SAVE UNIQUE VEHICLE
                    # --------------------------------------------------

                    if vehicle_id not in saved_vehicles:

                        saved_vehicles.add(vehicle_id)

                        total_vehicles += 1

                        vehicle_counts[vehicle_type] += 1

                        vehicle_data = {
                            "vehicle_id": vehicle_id,
                            "vehicle_type": vehicle_type,
                            "vehicle_color": vehicle_color
                        }

                        try:

                            save_vehicle(vehicle_data)

                            print(
                                f"Saved vehicle {vehicle_id}: "
                                f"{vehicle_type} ({vehicle_color})"
                            )

                        except Exception as error:

                            print(
                                "Vehicle database error:",
                                error
                            )

                    # --------------------------------------------------
                    # LINE CROSSING DETECTION
                    # --------------------------------------------------

                    previous_y = previous_positions.get(vehicle_id)

                    if previous_y is not None:

                        crossed = (
                            previous_y < line_y <= center_y
                            or
                            previous_y > line_y >= center_y
                        )

                        if crossed and vehicle_id not in crossed_vehicles:

                            crossed_vehicles.add(vehicle_id)

                            direction = (
                                "DOWN"
                                if center_y > previous_y
                                else "UP"
                            )

                            event_time = datetime.now()

                            total_crossings += 1

                            event_data = {
                                "vehicle_id": vehicle_id,
                                "vehicle_type": vehicle_type,
                                "vehicle_color": vehicle_color,
                                "direction": direction,
                                "timestamp": event_time
                            }

                            try:

                                save_crossing_event(event_data)

                                print(
                                    f"Vehicle {vehicle_id} crossed "
                                    f"{direction}: {vehicle_type} "
                                    f"({vehicle_color})"
                                )

                            except Exception as error:

                                print(
                                    "Crossing database error:",
                                    error
                                )

                            csv_writer.writerow([
                                vehicle_id,
                                vehicle_type,
                                vehicle_color,
                                direction,
                                event_time.isoformat()
                            ])

                            csv_file.flush()

                    previous_positions[vehicle_id] = center_y

                    # --------------------------------------------------
                    # DRAW BOUNDING BOX
                    # --------------------------------------------------

                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    label = (
                        f"{vehicle_type} | "
                        f"{vehicle_color} | ID:{vehicle_id}"
                    )

                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 0),
                        2
                    )

                    # Vehicle center
                    cv2.circle(
                        annotated_frame,
                        (center_x, center_y),
                        4,
                        (255, 0, 0),
                        -1
                    )

            # --------------------------------------------------
            # DRAW LIVE COUNTERS
            # --------------------------------------------------

            cv2.putText(
                annotated_frame,
                f"Total Vehicles: {total_vehicles}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Crossings: {total_crossings}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Cars: {vehicle_counts['Car']}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Buses: {vehicle_counts['Bus']}",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Trucks: {vehicle_counts['Truck']}",
                (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Motorcycles: {vehicle_counts['Motorcycle']}",
                (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # --------------------------------------------------
            # SAVE OUTPUT VIDEO
            # --------------------------------------------------

            video_writer.write(annotated_frame)

            # --------------------------------------------------
            # PUBLISH FRAME TO REACT
            # --------------------------------------------------

            success, encoded_frame = cv2.imencode(
                ".jpg",
                annotated_frame,
                [cv2.IMWRITE_JPEG_QUALITY, 85]
            )

            if success:

                publish_frame(encoded_frame.tobytes())

            # --------------------------------------------------
            # PUBLISH LIVE STATISTICS
            # --------------------------------------------------

            publish_stats({

                "status": "running",

                "total_vehicles": total_vehicles,

                "cars": vehicle_counts["Car"],

                "buses": vehicle_counts["Bus"],

                "trucks": vehicle_counts["Truck"],

                "motorcycles": vehicle_counts["Motorcycle"],

                "total_crossings": total_crossings,

                "active_vehicles": current_visible,

                "vehicle_counts": vehicle_counts.copy()

            })

            # Small delay to avoid unnecessary CPU usage
            time.sleep(0.001)

    finally:

        # --------------------------------------------------
        # RELEASE RESOURCES
        # --------------------------------------------------

        cap.release()

        video_writer.release()

        csv_file.close()

        print("Video resources released.")

        print("Detection stopped.")
