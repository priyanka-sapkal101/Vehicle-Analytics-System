import cv2
import csv
import sys
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

# Import PostgreSQL database function
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_connection import save_crossing_event, save_vehicle

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_PATH = BASE_DIR / "videos" / "traffic.webm"
OUTPUT_PATH = BASE_DIR / "outputs" / "vehicle_detection.mp4"
CSV_PATH = BASE_DIR / "outputs" / "line_crossing_events.csv"

# COCO vehicle class IDs
VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Counting line position (percentage of frame height)
LINE_POSITION = 0.55



def classify_vehicle_color(vehicle_crop):
    """
    Estimate dominant vehicle colour using HSV masks.
    """

    if vehicle_crop is None or vehicle_crop.size == 0:
        return "Unknown"

    height, width = vehicle_crop.shape[:2]

    if height < 10 or width < 10:
        return "Unknown"

    # Crop the central body area
    x1 = int(width * 0.15)
    x2 = int(width * 0.85)
    y1 = int(height * 0.25)
    y2 = int(height * 0.75)

    center_crop = vehicle_crop[y1:y2, x1:x2]

    if center_crop.size == 0:
        return "Unknown"

    # Resize for more stable colour estimation
    center_crop = cv2.resize(center_crop, (100, 100))

    hsv = cv2.cvtColor(center_crop, cv2.COLOR_BGR2HSV)

    import numpy as np

    # HSV colour ranges
    masks = {
        "Red": (
            cv2.inRange(hsv, np.array([0, 80, 50]),
                        np.array([10, 255, 255])) |
            cv2.inRange(hsv, np.array([170, 80, 50]),
                        np.array([180, 255, 255]))
        ),

        "Yellow": cv2.inRange(
            hsv, np.array([15, 80, 80]),
            np.array([35, 255, 255])
        ),

        "Green": cv2.inRange(
            hsv, np.array([36, 50, 40]),
            np.array([85, 255, 255])
        ),

        "Blue": cv2.inRange(
            hsv, np.array([90, 60, 40]),
            np.array([135, 255, 255])
        ),

        "White": cv2.inRange(
            hsv, np.array([0, 0, 170]),
            np.array([180, 65, 255])
        ),

        "Black": cv2.inRange(
            hsv, np.array([0, 0, 0]),
            np.array([180, 255, 55])
        ),

        "Silver/Grey": cv2.inRange(
            hsv, np.array([0, 0, 56]),
            np.array([180, 65, 169])
        )
    }

    # Calculate percentage of each colour
    total_pixels = hsv.shape[0] * hsv.shape[1]

    percentages = {
        name: cv2.countNonZero(mask) / total_pixels * 100
        for name, mask in masks.items()
    }

    best_color = max(percentages, key=percentages.get)

    # Avoid assigning a colour when no mask is sufficiently dominant
    if percentages[best_color] < 8:
        return "Other"

    return best_color


def main():
    if not VIDEO_PATH.exists():
        print(f"Video not found: {VIDEO_PATH}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Loading YOLO model...")
    model = YOLO("yolo11n.pt")

    print("Opening traffic video...")
    cap = cv2.VideoCapture(str(VIDEO_PATH))

    if not cap.isOpened():
        print("ERROR: Could not open video.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    # Horizontal counting line
    counting_line_y = int(height * LINE_POSITION)

    writer = cv2.VideoWriter(
        str(OUTPUT_PATH),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    if not writer.isOpened():
        print("ERROR: Could not create output video.")
        cap.release()
        return

    vehicle_ids = set()

    vehicle_counts = {
        "Car": 0,
        "Motorcycle": 0,
        "Bus": 0,
        "Truck": 0
    }

    # Store previous centre positions
    previous_positions = {}

    # Prevent counting the same tracked ID more than once
    counted_ids = set()
    saved_vehicle_ids = set()

    crossing_events = []

    print("Vehicle detection and line counting started!")
    print("Press Q to stop.")

    while True:
        success, frame = cap.read()

        if not success:
            break

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=list(VEHICLE_CLASSES.keys()),
            conf=0.40,
            imgsz=640,
            verbose=False
        )

        annotated_frame = frame.copy()

        for result in results:
            boxes = result.boxes

            if boxes is None:
                continue

            for box in boxes:
                class_id = int(box.cls[0])
                vehicle_name = VEHICLE_CLASSES[class_id]

                x1, y1, x2, y2 = map(
                    int, box.xyxy[0].tolist()
                )
                
                
                vehicle_crop = frame[y1:y2, x1:x2]

                
                            
                vehicle_color = classify_vehicle_color(vehicle_crop)

                track_id = None

                if box.id is not None:
                    track_id = int(box.id[0])

                    # Count each unique vehicle only once
                    if track_id not in vehicle_ids:
                        vehicle_ids.add(track_id)
                        vehicle_counts[vehicle_name] += 1

                    # Save each unique vehicle to PostgreSQL
                    if track_id not in saved_vehicle_ids:
                        if save_vehicle(track_id, vehicle_name, vehicle_color):
                            saved_vehicle_ids.add(track_id)
                            print(f"Saved vehicle {track_id} to PostgreSQL")


                # Vehicle centre point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                if track_id is not None:
                    previous_y = previous_positions.get(track_id)

                    if previous_y is not None and track_id not in counted_ids:

                        direction = None

                        if previous_y < counting_line_y <= center_y:
                            direction = "DOWN"

                        elif previous_y > counting_line_y >= center_y:
                            direction = "UP"

                        if direction:
                            counted_ids.add(track_id)

                            event = {
                                "vehicle_id": track_id,
                                "vehicle_type": vehicle_name,
                                "vehicle_color": vehicle_color,
                                "direction": direction,
                                "timestamp": datetime.now().isoformat(
                                    timespec="seconds"
                                )
                            }
                            
                            crossing_events.append(event)

                            # Save vehicle crossing event to PostgreSQL
                            save_crossing_event(event)

                            print(
                                f"Vehicle {track_id} crossed "
                                f"{direction}: {vehicle_name} ({vehicle_color})"
                                )

                            

                    previous_positions[track_id] = center_y

                # Draw vehicle bounding box
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                label = f"{vehicle_name} | {vehicle_color}"

                if track_id is not None:
                    label += f" ID:{track_id}"

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    annotated_frame,
                    (center_x, center_y),
                    4,
                    (255, 0, 0),
                    -1
                )

        # Draw horizontal counting line
        cv2.line(
            annotated_frame,
            (0, counting_line_y),
            (width, counting_line_y),
            (0, 0, 255),
            3
        )

        cv2.putText(
            annotated_frame,
            "VEHICLE COUNTING LINE",
            (20, counting_line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        # Display statistics
        y = 30

        cv2.putText(
            annotated_frame,
            f"Total unique vehicles: {len(vehicle_ids)}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        for name, count in vehicle_counts.items():
            y += 28
            cv2.putText(
                annotated_frame,
                f"{name}: {count}",
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

        y += 28
        cv2.putText(
            annotated_frame,
            f"Line crossings: {len(crossing_events)}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        writer.write(annotated_frame)

        cv2.imshow(
            "Vehicle Analytics - Line Crossing",
            annotated_frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    # Save crossing events to CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "vehicle_id",
            "vehicle_type",
            "vehicle_color",
            "direction",
            "timestamp"
        ]

        csv_writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        csv_writer.writeheader()
        csv_writer.writerows(crossing_events)

    print("\n========== VEHICLE ANALYTICS REPORT ==========")
    print(f"Total unique vehicles: {len(vehicle_ids)}")

    for name, count in vehicle_counts.items():
        print(f"{name}: {count}")

    print(f"Total line crossings: {len(crossing_events)}")
    print(f"Processed video: {OUTPUT_PATH}")
    print(f"Crossing events CSV: {CSV_PATH}")

    print("\nVehicle analytics completed!")


if __name__ == "__main__":
    main()
