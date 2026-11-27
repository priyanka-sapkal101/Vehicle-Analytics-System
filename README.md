# 🚗 Vehicle Analytics System

An AI-powered **Vehicle Analytics System** that uses Computer Vision and Deep Learning to detect, track, classify, and analyze vehicles from traffic video streams. The system provides real-time vehicle monitoring, traffic statistics, and an interactive analytics dashboard.

## 📌 Project Overview

The Vehicle Analytics System combines YOLO11 object detection, Python, FastAPI, PostgreSQL, and React to monitor traffic and generate meaningful vehicle analytics.

It is designed to detect different types of vehicles, track their movement, count vehicles crossing a virtual line, and store vehicle information in a database for further analysis.

## ✨ Features

- **Vehicle Detection:** Detects vehicles using the YOLO11 deep learning model.
- **Vehicle Classification:** Identifies vehicle categories such as cars, buses, trucks, and motorcycles.
- **Vehicle Tracking:** Tracks detected vehicles across video frames.
- **Vehicle Counting:** Counts vehicles crossing a virtual counting line.
- **Direction Detection:** Identifies vehicle movement direction (UP/DOWN).
- **Vehicle Color Detection:** Identifies vehicle colors.
- **Database Integration:** Stores vehicle detection records in PostgreSQL.
- **REST API:** Uses FastAPI to connect the detection system with the frontend.
- **Interactive Dashboard:** Displays vehicle analytics using React.
- **Data Visualization:** Provides charts and statistics for traffic analysis.
- **Video Analytics:** Processes traffic videos for vehicle monitoring.
- **NVIDIA DeepStream Configuration:** Includes configuration files for YOLO11-based DeepStream inference and analytics.
- **Media Streaming Configuration:** Includes MediaMTX configuration for video streaming workflows.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development and vehicle detection |
| YOLO11 | Vehicle object detection |
| OpenCV | Video processing and computer vision |
| ONNX | Deep learning model format |
| NVIDIA DeepStream | GPU-accelerated video analytics |
| FastAPI | REST API development |
| PostgreSQL | Database management |
| React.js | Frontend development |
| JavaScript | Frontend functionality |
| Recharts | Data visualization |
| CSS | Dashboard styling |
| MediaMTX | Media streaming |

## 📂 Project Structure

```text
Vehicle-Analytics-System/
│
├── backend/
│   └── main.py
│
├── database/
│   └── db_connection.py
│
├── deepstream/
│   ├── configs/
│   │   ├── config_infer_primary_yolo11.txt
│   │   ├── config_nvdsanalytics.txt
│   │   ├── config_tracker.txt
│   │   └── deepstream_app_config.txt
│   │
│   ├── src/
│   │   └── nvdsparse_yolo11.cpp
│   │
│   └── labels.txt
│
├── detection/
│   ├── vehicle_detector.py
│   └── yolo11n.onnx
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── videos/
│   └── traffic.webm
│
├── mediamtx.yml
├── .gitignore
├── LICENSE
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/priyanka-sapkal101/Vehicle-Analytics-System.git
```

Navigate into the project:

```bash
cd Vehicle-Analytics-System
```

### 2. Create a Python Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install ultralytics opencv-python numpy fastapi uvicorn psycopg2-binary
```

Install any additional dependencies required by your project.

### 4. Configure PostgreSQL

1. Install PostgreSQL.
2. Create a database for the project.
3. Configure your database connection in `database/db_connection.py`.
4. Ensure the database server is running before starting vehicle detection.

### 5. Run Vehicle Detection

From the project root directory:

```bash
python detection/vehicle_detector.py
```

The detection system processes the traffic video and records vehicle information in PostgreSQL.

### 6. Start the FastAPI Backend

Open another terminal, activate the virtual environment, and run:

```bash
uvicorn backend.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the React Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in your terminal (usually):

```text
http://localhost:5173
```

## 📊 System Architecture

```text
       Traffic Video / Camera
                 |
                 v
          YOLO11 Detection
                 |
                 v
          Vehicle Tracking
                 |
                 v
       Vehicle Classification
                 |
                 v
       Direction and Line Counting
                 |
                 v
          PostgreSQL Database
                 |
                 v
             FastAPI
                 |
                 v
           React Dashboard
                 |
                 v
        Traffic Analytics
```

## 📈 Dashboard Analytics

The React dashboard is designed to present vehicle information through visual charts and statistics.

Analytics include:

- Total vehicles detected.
- Vehicle category distribution.
- Car, bus, truck, and motorcycle counts.
- Vehicle movement direction.
- Vehicle color information.
- Traffic monitoring statistics.

## 🧠 Deep Learning Model

This project uses the YOLO11 object detection architecture.

**Model:** YOLO11n (ONNX format)

**Model file:** `detection/yolo11n.onnx`

YOLO11 is used for identifying objects in traffic video frames. The ONNX model is also included in the DeepStream inference configuration.

## 🚀 Future Enhancements

- Real-time CCTV camera integration.
- Live traffic monitoring.
- Traffic congestion detection.
- Vehicle speed estimation.
- Number plate recognition (ANPR).
- Accident detection.
- Traffic violation detection.
- Advanced traffic reporting.
- Multi-camera vehicle tracking.
- Cloud-based deployment.

## 💻 Requirements

- Python 3.10 or later (use a version compatible with the selected dependencies).
- Node.js and npm.
- PostgreSQL.
- OpenCV-compatible video input.
- YOLO11 model in ONNX format.
- NVIDIA GPU and compatible DeepStream environment for GPU-accelerated DeepStream execution.

**Note:** The Python/OpenCV detection workflow and NVIDIA DeepStream workflow have different environment requirements. DeepStream generally requires a compatible NVIDIA GPU, drivers, CUDA, and supported DeepStream installation.

## 👩‍💻 Author

**Priyanka Anil Sapkal**

GitHub: https://github.com/priyanka-sapkal101/Vehicle-Analytics-System

## 📜 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

⭐ If you find this project interesting, consider giving it a star on GitHub!
