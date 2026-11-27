# 🚗 Vehicle Analytics System

An AI-powered real-time Vehicle Analytics System that uses **YOLO11, OpenCV, FastAPI, React, and PostgreSQL** to detect, track, count, and analyze vehicles from traffic video footage.

The system provides a modern React dashboard where users can start and stop vehicle detection, watch annotated video footage, monitor live vehicle counts, and view analytics.

## ✨ Features

### 1. AI-Based Vehicle Detection
- Detects vehicles using the YOLO11n object detection model.
- Identifies four vehicle categories:
  - Cars
  - Motorcycles
  - Buses
  - Trucks
- Uses OpenCV for video processing.

### 2. Vehicle Tracking
- Tracks detected vehicles using ByteTrack.
- Assigns tracking IDs to detected vehicles.
- Identifies vehicle movement across a predefined counting line.

### 3. Live Vehicle Counting
- Counts unique detected vehicles.
- Tracks vehicle crossings.
- Displays live statistics for:
  - Total vehicles
  - Cars
  - Buses
  - Trucks
  - Motorcycles
  - Active vehicles
  - Total crossings

### 4. Live Video Streaming
- Displays processed traffic footage directly on the React dashboard.
- Shows bounding boxes around detected vehicles.
- Displays vehicle IDs, vehicle types, and estimated colors.
- Streams annotated video from the FastAPI backend.
- No separate OpenCV output window is required.

### 5. Interactive Dashboard
- Start Detection button to start vehicle detection.
- Stop Detection button to stop vehicle detection.
- Live vehicle statistics.
- Vehicle type analytics.
- Vehicle color analytics.
- Recent vehicle crossing events.
- Direction-wise vehicle analytics.
- Automatic dashboard data refresh.

### 6. PostgreSQL Database Integration
- Stores detected vehicle information.
- Stores vehicle crossing events.
- Retrieves stored data for dashboard analytics.
- Maintains historical vehicle information.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend and detection logic |
| YOLO11n | Vehicle detection |
| OpenCV | Video processing and annotation |
| ByteTrack | Vehicle tracking |
| FastAPI | Backend API and video streaming |
| PostgreSQL | Database management |
| React.js | Frontend dashboard |
| JavaScript | Frontend functionality |
| Recharts | Data visualization |
| Lucide React | Dashboard icons |
| HTML5 & CSS3 | Dashboard design |

## 📂 Project Structure

```text
Vehicle-Analytics-System/
│
├── backend/
│   ├── main.py
│   └── stream_manager.py
│
├── database/
│   └── db_connection.py
│
├── detection/
│   └── vehicle_detector.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
│
├── videos/
│   └── traffic.webm
│
├── outputs/
│   ├── vehicle_detection.mp4
│   └── line_crossing_events.csv
│
├── venv/
├── .gitignore
├── README.md
└── requirements.txt
```

*Generated files and local environment folders may be excluded from Git using `.gitignore`.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.10 or later
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/priyanka-sapkal101/Vehicle-Analytics-System.git
```

Navigate into the project:

```bash
cd Vehicle-Analytics-System
```

### 2. Create and Activate Python Virtual Environment

```bash
python -m venv venv
```

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

- Install and start PostgreSQL.
- Create the database required by the project.
- Configure your database connection settings in `database/db_connection.py`.
- Ensure the required database tables are available.

### 5. Prepare the Traffic Video

Place your traffic video inside the `videos` folder.

The default input video is:

```text
videos/traffic.webm
```

The YOLO11n model weights (`yolo11n.pt`) should also be available to the detection script. Ultralytics can download the weights when they are not already present.

### 6. Start the FastAPI Backend

From the project root directory:

```bash
python -m uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the React Frontend

Open another terminal:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

Open the dashboard in your browser using the URL displayed by Vite, usually:

```text
http://localhost:5173
```

## ▶️ How to Use

1. Start PostgreSQL.
2. Run the FastAPI backend.
3. Start the React frontend.
4. Open the dashboard in your browser.
5. Click **Start Detection**.
6. Watch the processed traffic video directly on the dashboard.
7. Monitor vehicle detection, tracking, and live counts.
8. View vehicle analytics and recent crossing events.
9. Click **Stop Detection** when you want to stop processing.

## 🔗 Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend health check |
| GET | `/analytics/summary` | Vehicle summary |
| GET | `/analytics/colors` | Vehicle color analytics |
| GET | `/analytics/types` | Vehicle type analytics |
| GET | `/analytics/recent` | Recent crossing events |
| POST | `/events/crossing` | Save crossing event |
| POST | `/detection/start` | Start vehicle detection |
| POST | `/detection/stop` | Stop vehicle detection |
| GET | `/detection/stream` | Stream annotated video |
| GET | `/detection/stats` | Get live detection statistics |

## 📊 System Workflow

```text
Traffic Video
     |
     v
YOLO11 Vehicle Detection
     |
     v
ByteTrack Vehicle Tracking
     |
     v
Vehicle Classification
     |
     v
Vehicle Counting and Line Crossing
     |
     v
FastAPI Backend
     |
     +------------------+
     |                  |
     v                  v
PostgreSQL        Live Video Stream
     |                  |
     v                  v
Analytics API     React Dashboard
     |                  |
     +--------+---------+
              |
              v
       Vehicle Analytics
```

## 🎯 Project Objective

The main objective of this project is to develop an AI-powered traffic monitoring and analytics system that automates vehicle detection, tracking, counting, and data analysis.

It demonstrates how computer vision, machine learning, backend development, database management, and frontend technologies can work together to build a practical intelligent transportation application.

## 🚀 Future Improvements

- Real-time detection from CCTV cameras.
- Multiple camera support.
- Traffic congestion monitoring.
- Vehicle speed estimation.
- Number plate recognition.
- Downloadable analytics reports.
- Advanced traffic pattern analysis.

## 👩‍💻 Author

**Priyanka Sapkal**

GitHub: [priyanka-sapkal101](https://github.com/priyanka-sapkal101)

---

⭐ If you find this project interesting, consider giving the repository a star!
