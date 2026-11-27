
import threading
import time

from detection.vehicle_detector import run_detection


# --------------------------------------------------
# THREAD MANAGEMENT
# --------------------------------------------------

lock = threading.Lock()

stop_event = None
worker_thread = None

latest_frame = None


# --------------------------------------------------
# LIVE DETECTION STATISTICS
# --------------------------------------------------

stats = {
    "status": "stopped",
    "total_vehicles": 0,
    "cars": 0,
    "buses": 0,
    "trucks": 0,
    "motorcycles": 0,
    "total_crossings": 0,
    "active_vehicles": 0,
    "message": None
}


# --------------------------------------------------
# UPDATE LATEST VIDEO FRAME
# --------------------------------------------------

def update_frame(frame):

    global latest_frame

    with lock:
        latest_frame = frame


# --------------------------------------------------
# UPDATE LIVE STATISTICS
# --------------------------------------------------

def update_stats(new_stats):

    with lock:
        stats.update(new_stats)


# --------------------------------------------------
# GET LIVE STATISTICS
# --------------------------------------------------

def get_stats():

    with lock:
        result = stats.copy()

    return result


# --------------------------------------------------
# START VEHICLE DETECTION
# --------------------------------------------------

def start_detection():

    global stop_event
    global worker_thread
    global latest_frame

    # Check whether detection is already running
    if worker_thread and worker_thread.is_alive():

        return False, "Detection is already running."

    # Create a new stop event
    stop_event = threading.Event()

    # Reset previous video frame and statistics
    with lock:

        latest_frame = None

        stats.update({
            "status": "starting",
            "total_vehicles": 0,
            "cars": 0,
            "buses": 0,
            "trucks": 0,
            "motorcycles": 0,
            "total_crossings": 0,
            "active_vehicles": 0,
            "message": None
        })

    # --------------------------------------------------
    # BACKGROUND DETECTION WORKER
    # --------------------------------------------------

    def worker():

        failed = False

        try:

            update_stats({
                "status": "running",
                "message": None
            })

            print("Vehicle detection started.")

            # Run YOLO detection
            run_detection(
                stop_event=stop_event,
                publish_frame=update_frame,
                publish_stats=update_stats
            )

            print("Vehicle detection finished.")

        except Exception as error:

            failed = True

            print("Detection error:", error)

            update_stats({
                "status": "error",
                "message": str(error)
            })

        finally:

            if not failed:

                update_stats({
                    "status": "stopped"
                })

            print("Detection worker stopped.")

    # --------------------------------------------------
    # CREATE AND START BACKGROUND THREAD
    # --------------------------------------------------

    worker_thread = threading.Thread(
        target=worker,
        daemon=True
    )

    worker_thread.start()

    return True, "Vehicle detection started successfully."


# --------------------------------------------------
# STOP VEHICLE DETECTION
# --------------------------------------------------

def stop_detection():

    global stop_event

    if worker_thread and worker_thread.is_alive():

        if stop_event:
            stop_event.set()

        return True, "Stopping vehicle detection."

    return False, "Detection is not running."


# --------------------------------------------------
# LIVE MJPEG VIDEO STREAM
# --------------------------------------------------

def video_stream():

    while True:

        with lock:
            frame = latest_frame

        if frame is not None:

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode() +
                b"\r\n\r\n" +
                frame +
                b"\r\n"
            )

        time.sleep(0.05)
