
import psycopg2
import os


def get_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="vehicle_analytics",
            user="postgres",
            password=os.environ["DB_PASSWORD"],
            port="5432"
        )
        return connection

    except Exception as error:
        print("Database connection failed:", error)
        return None


def save_crossing_event(event):
    connection = get_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        # Insert or update vehicle information
        cursor.execute(
            """
            INSERT INTO vehicles
                (vehicle_id, vehicle_type, vehicle_color)
            VALUES (%s, %s, %s)
            ON CONFLICT (vehicle_id)
            DO UPDATE SET
                vehicle_type = EXCLUDED.vehicle_type,
                vehicle_color = EXCLUDED.vehicle_color
            """,
            (
                event["vehicle_id"],
                event["vehicle_type"],
                event["vehicle_color"]
            )
        )

        # Insert crossing event
        cursor.execute(
            """
            INSERT INTO crossing_events
                (vehicle_id, direction, event_timestamp)
            VALUES (%s, %s, %s)
            """,
            (
                event["vehicle_id"],
                event["direction"],
                event["timestamp"]
            )
        )

        connection.commit()
        print(
            f"Saved vehicle {event['vehicle_id']} to PostgreSQL"
        )

        return True

    except Exception as error:
        connection.rollback()
        print("Error saving vehicle event:", error)
        return False

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    connection = get_connection()

    if connection:
        print("PostgreSQL connected successfully!")
        connection.close()
        print("Database connection closed.")

def save_vehicle(vehicle_id, vehicle_type, vehicle_color):
    """
    Save each uniquely detected vehicle to PostgreSQL.
    """
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO vehicles
                (vehicle_id, vehicle_type, vehicle_color)
            VALUES (%s, %s, %s)
            ON CONFLICT (vehicle_id)
            DO UPDATE SET
                vehicle_type = EXCLUDED.vehicle_type,
                vehicle_color = EXCLUDED.vehicle_color
            """,
            (vehicle_id, vehicle_type, vehicle_color)
        )

        connection.commit()
        return True

    except Exception as error:
        connection.rollback()
        print("Error saving vehicle:", error)
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()
