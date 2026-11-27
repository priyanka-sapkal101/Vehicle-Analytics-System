
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from database.db_connection import get_connection, save_crossing_event

from backend.stream_manager import (
    start_detection as start_detection_worker,
    stop_detection as stop_detection_worker,
    get_stats,
    video_stream
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Vehicle Analytics API",
    description="Real-Time Vehicle Analytics System",
    version="1.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Vehicle Analytics API is running!"
    }


# --------------------------------------------------
# ANALYTICS: SUMMARY
# --------------------------------------------------

@app.get("/analytics/summary")
def get_summary():

    connection = get_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_vehicles,

                COUNT(*) FILTER (
                    WHERE vehicle_type = 'Car'
                ) AS cars,

                COUNT(*) FILTER (
                    WHERE vehicle_type = 'Bus'
                ) AS buses,

                COUNT(*) FILTER (
                    WHERE vehicle_type = 'Truck'
                ) AS trucks,

                COUNT(*) FILTER (
                    WHERE vehicle_type = 'Motorcycle'
                ) AS motorcycles

            FROM vehicles
        """)

        vehicle_data = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*)
            FROM crossing_events
        """)

        total_crossings = cursor.fetchone()[0]

        cursor.close()

        return {
            "total_vehicles": vehicle_data[0],
            "cars": vehicle_data[1],
            "buses": vehicle_data[2],
            "trucks": vehicle_data[3],
            "motorcycles": vehicle_data[4],
            "total_crossings": total_crossings
        }

    finally:
        connection.close()


# --------------------------------------------------
# ANALYTICS: VEHICLE COLORS
# --------------------------------------------------

@app.get("/analytics/colors")
def get_colors():

    connection = get_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                vehicle_color,
                COUNT(*)
            FROM vehicles
            GROUP BY vehicle_color
            ORDER BY COUNT(*) DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return {
            "colors": [
                {
                    "color": row[0],
                    "count": row[1]
                }
                for row in rows
            ]
        }

    finally:
        connection.close()


# --------------------------------------------------
# ANALYTICS: VEHICLE TYPES
# --------------------------------------------------

@app.get("/analytics/types")
def get_types():

    connection = get_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                vehicle_type,
                COUNT(*)
            FROM vehicles
            GROUP BY vehicle_type
            ORDER BY COUNT(*) DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return {
            "vehicle_types": [
                {
                    "type": row[0],
                    "count": row[1]
                }
                for row in rows
            ]
        }

    finally:
        connection.close()


# --------------------------------------------------
# ANALYTICS: RECENT CROSSING EVENTS
# --------------------------------------------------

@app.get("/analytics/recent")
def get_recent_events():

    connection = get_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                ce.event_id,
                ce.vehicle_id,
                v.vehicle_type,
                v.vehicle_color,
                ce.direction,
                ce.event_timestamp

            FROM crossing_events ce

            LEFT JOIN vehicles v
                ON ce.vehicle_id = v.vehicle_id

            ORDER BY ce.event_timestamp DESC

            LIMIT 20
        """)

        rows = cursor.fetchall()

        cursor.close()

        return {
            "recent_events": [
                {
                    "event_id": row[0],
                    "vehicle_id": row[1],
                    "vehicle_type": row[2],
                    "vehicle_color": row[3],
                    "direction": row[4],
                    "timestamp": (
                        row[5].isoformat()
                        if row[5]
                        else None
                    )
                }
                for row in rows
            ]
        }

    finally:
        connection.close()


# --------------------------------------------------
# CROSSING EVENT MODEL
# --------------------------------------------------

class CrossingEvent(BaseModel):

    vehicle_id: int

    vehicle_type: Literal[
        "Car",
        "Bus",
        "Truck",
        "Motorcycle"
    ]

    vehicle_color: str

    direction: Literal[
        "UP",
        "DOWN"
    ]

    timestamp: datetime


# --------------------------------------------------
# RECEIVE VEHICLE CROSSING EVENT
# --------------------------------------------------

@app.post("/events/crossing")
def receive_crossing_event(event: CrossingEvent):

    event_data = event.model_dump()

    success = save_crossing_event(event_data)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to save crossing event"
        )

    return {
        "status": "success",
        "message": "Vehicle crossing event saved successfully",
        "vehicle_id": event.vehicle_id,
        "direction": event.direction
    }


# --------------------------------------------------
# START VEHICLE DETECTION
# --------------------------------------------------

@app.post("/detection/start")
def start_vehicle_detection():

    success, message = start_detection_worker()

    if not success:
        raise HTTPException(
            status_code=409,
            detail=message
        )

    return {
        "status": "success",
        "message": message
    }


# --------------------------------------------------
# STOP VEHICLE DETECTION
# --------------------------------------------------

@app.post("/detection/stop")
def stop_vehicle_detection():

    success, message = stop_detection_worker()

    if not success:
        raise HTTPException(
            status_code=409,
            detail=message
        )

    return {
        "status": "success",
        "message": message
    }


# --------------------------------------------------
# LIVE VEHICLE DETECTION VIDEO STREAM
# --------------------------------------------------

@app.get("/detection/stream")
def get_detection_stream():

    return StreamingResponse(
        video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------
# LIVE VEHICLE DETECTION STATISTICS
# --------------------------------------------------

@app.get("/detection/stats")
def get_detection_stats():

    return get_stats()
