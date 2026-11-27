from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from database.db_connection import get_connection, save_crossing_event

app = FastAPI(
    title="Vehicle Analytics API",
    description="Real-Time Vehicle Analytics System",
    version="1.0"
)

# Allow frontend applications to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Vehicle Analytics API is running!"
    }


@app.get("/analytics/summary")
def get_summary():
    connection = get_connection()
    if connection is None:
        return {"error": "Database connection failed"}

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

        cursor.execute("SELECT COUNT(*) FROM crossing_events")
        total_crossings = cursor.fetchone()[0]

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


@app.get("/analytics/colors")
def get_colors():
    connection = get_connection()
    if connection is None:
        return {"error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT vehicle_color, COUNT(*)
            FROM vehicles
            GROUP BY vehicle_color
            ORDER BY COUNT(*) DESC
        """)

        rows = cursor.fetchall()

        return {
            "colors": [
                {"color": row[0], "count": row[1]}
                for row in rows
            ]
        }

    finally:
        connection.close()


@app.get("/analytics/types")
def get_types():
    connection = get_connection()
    if connection is None:
        return {"error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT vehicle_type, COUNT(*)
            FROM vehicles
            GROUP BY vehicle_type
            ORDER BY COUNT(*) DESC
        """)

        rows = cursor.fetchall()

        return {
            "vehicle_types": [
                {"type": row[0], "count": row[1]}
                for row in rows
            ]
        }

    finally:
        connection.close()


@app.get("/analytics/recent")
def get_recent_events():
    connection = get_connection()
    if connection is None:
        return {"error": "Database connection failed"}

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

        return {
            "recent_events": [
                {
                    "event_id": row[0],
                    "vehicle_id": row[1],
                    "vehicle_type": row[2],
                    "vehicle_color": row[3],
                    "direction": row[4],
                    "timestamp": row[5].isoformat()
                }
                for row in rows
            ]
        }

    finally:
        connection.close()
# DeepStream crossing event structure
class CrossingEvent(BaseModel):
    vehicle_id: int
    vehicle_type: Literal["Car", "Bus", "Truck", "Motorcycle"]
    vehicle_color: str
    direction: Literal["UP", "DOWN"]
    timestamp: datetime


# Receive vehicle crossing events from DeepStream
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