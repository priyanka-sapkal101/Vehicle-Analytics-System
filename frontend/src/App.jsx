
import { useEffect, useState } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  CartesianGrid
} from "recharts";

import {
  Car,
  Bus,
  Truck,
  Bike,
  Activity,
  RefreshCw,
  Clock,
  AlertCircle,
  Camera,
  ShieldCheck,
  Radio,
  ArrowUpRight,
  ArrowDownRight,
  ArrowLeftRight,
  Server,
  Eye,
  Gauge,
  CircleDot
} from "lucide-react";

import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {

  // Dashboard states
  const [summary, setSummary] = useState({});
  const [colors, setColors] = useState([]);
  const [types, setTypes] = useState([]);
  const [recent, setRecent] = useState([]);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [lastUpdated, setLastUpdated] = useState(null);
  const [connected, setConnected] = useState(false);

  // Video states
  const [videoReady, setVideoReady] = useState(false);
  const [videoError, setVideoError] = useState(false);

  // Detection states
  const [detectionStatus, setDetectionStatus] = useState("stopped");
  const [detectionStats, setDetectionStats] = useState({});
  const [detectionLoading, setDetectionLoading] = useState(false);


  // ==========================================
  // LOAD DATABASE ANALYTICS
  // ==========================================

  const loadDashboard = async () => {
    try {
      setError("");
      setLoading(true);

      const [s, c, t, r] = await Promise.all([
        fetch(`${API}/analytics/summary`),
        fetch(`${API}/analytics/colors`),
        fetch(`${API}/analytics/types`),
        fetch(`${API}/analytics/recent`)
      ]);

      if (![s, c, t, r].every(response => response.ok)) {
        throw new Error("Could not load dashboard data.");
      }

      const [
        summaryData,
        colorData,
        typeData,
        recentData
      ] = await Promise.all([
        s.json(),
        c.json(),
        t.json(),
        r.json()
      ]);

      setSummary(summaryData);
      setColors(colorData.colors || []);
      setTypes(typeData.vehicle_types || []);
      setRecent(recentData.recent_events || []);

      setLastUpdated(new Date());
      setConnected(true);

    } catch (err) {

      setError(err.message + " Make sure FastAPI is running.");
      setConnected(false);

    } finally {
      setLoading(false);
    }
  };


  // ==========================================
  // LOAD LIVE DETECTION STATISTICS
  // ==========================================

  const loadDetectionStats = async () => {
    try {
      const response = await fetch(`${API}/detection/stats`);

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      setDetectionStats(data);

      setDetectionStatus(data.status || "stopped");

    } catch (err) {
      console.error("Detection stats error:", err);
    }
  };


  // ==========================================
  // START DETECTION
  // ==========================================

  const startDetection = async () => {

    try {
      setDetectionLoading(true);
      setError("");

      const response = await fetch(`${API}/detection/start`, {
        method: "POST"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not start detection."
        );
      }

      setDetectionStatus("starting");
      setVideoReady(false);
      setVideoError(false);

      loadDetectionStats();

    } catch (err) {

      setError(err.message);

    } finally {
      setDetectionLoading(false);
    }
  };


  // ==========================================
  // STOP DETECTION
  // ==========================================

  const stopDetection = async () => {

    try {
      setDetectionLoading(true);
      setError("");

      const response = await fetch(`${API}/detection/stop`, {
        method: "POST"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not stop detection."
        );
      }

      setVideoReady(false);

    } catch (err) {

      setError(err.message);

    } finally {
      setDetectionLoading(false);
    }
  };


  // ==========================================
  // INITIAL DASHBOARD LOAD
  // ==========================================

  useEffect(() => {

    loadDashboard();
    loadDetectionStats();

    const dashboardTimer = setInterval(
      loadDashboard,
      5000
    );

    const detectionTimer = setInterval(
      loadDetectionStats,
      1000
    );

    return () => {
      clearInterval(dashboardTimer);
      clearInterval(detectionTimer);
    };

  }, []);


  // ==========================================
  // FORMAT NUMBERS
  // ==========================================

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN");


  // ==========================================
  // KPI CARDS
  // ==========================================

  const isDetectionRunning =
    detectionStatus === "running";

  const cards = [

    {
      title: "Total Vehicles",
      value: isDetectionRunning
        ? detectionStats.total_vehicles
        : summary.total_vehicles,
      icon: Car,
      color: "blue"
    },

    {
      title: "Total Crossings",
      value: isDetectionRunning
        ? detectionStats.total_crossings
        : summary.total_crossings,
      icon: Activity,
      color: "purple"
    },

    {
      title: "Cars",
      value: isDetectionRunning
        ? detectionStats.cars
        : summary.cars,
      icon: Car,
      color: "cyan"
    },

    {
      title: "Buses",
      value: isDetectionRunning
        ? detectionStats.buses
        : summary.buses,
      icon: Bus,
      color: "orange"
    },

    {
      title: "Trucks",
      value: isDetectionRunning
        ? detectionStats.trucks
        : summary.trucks,
      icon: Truck,
      color: "green"
    },

    {
      title: "Motorcycles",
      value: isDetectionRunning
        ? detectionStats.motorcycles
        : summary.motorcycles,
      icon: Bike,
      color: "pink"
    }

  ];


  // ==========================================
  // CHART COLORS
  // ==========================================

  const COLORS = [
    "#60a5fa",
    "#f59e0b",
    "#34d399",
    "#f87171",
    "#a78bfa",
    "#94a3b8",
    "#f472b6",
    "#2dd4bf"
  ];


  // ==========================================
  // DIRECTION ANALYTICS
  // ==========================================

  const directionCounts = recent.reduce((acc, item) => {

    const direction = String(
      item.direction || "Unknown"
    ).trim();

    acc[direction] = (acc[direction] || 0) + 1;

    return acc;

  }, {});


  const directionData = Object.entries(directionCounts)
    .map(([direction, count]) => ({
      direction,
      count
    }))
    .sort((a, b) => b.count - a.count);


  const directionIcons = [
    ArrowUpRight,
    ArrowDownRight,
    ArrowLeftRight
  ];


  const directionColors = [
    "direction-blue",
    "direction-green",
    "direction-purple",
    "direction-orange",
    "direction-cyan",
    "direction-pink"
  ];


  // ==========================================
  // RENDER DASHBOARD
  // ==========================================

  return (

    <main className="dashboard">

      {/* HEADER */}

      <header className="header">

        <div className="header-content">

          <div className="brand-icon">
            <Car size={28} />
          </div>

          <div>
            <h1>Vehicle Analytics</h1>
            <p>
              Intelligent Traffic Monitoring & Control
            </p>
          </div>

        </div>


        <div className="header-actions">

          <div
            className={`live-indicator ${
              connected ? "" : "offline"
            }`}
          >
            <span className="live-dot"></span>

            {connected
              ? "SYSTEM ONLINE"
              : "SYSTEM OFFLINE"}
          </div>


          <button
            onClick={loadDashboard}
            className={`refresh ${
              loading ? "refreshing" : ""
            }`}
            disabled={loading}
          >
            <RefreshCw size={17} />

            {loading
              ? "Updating..."
              : "Refresh"}
          </button>

        </div>

      </header>


      {/* STATUS BAR */}

      <section className="status-bar">

        <div className="status-left">
          <Activity size={17} />
          <span>Traffic Intelligence Overview</span>
        </div>


        <div className="status-right">
          <Clock size={15} />

          <span>
            Last updated:{" "}

            {lastUpdated
              ? lastUpdated.toLocaleTimeString()
              : "Waiting for data"}
          </span>
        </div>

      </section>


      {/* ERROR MESSAGE */}

      {error && (

        <div className="error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>

      )}


      {/* KPI CARDS */}

      <section className="stats">

        {cards.map(({
          title,
          value,
          icon: Icon,
          color
        }) => (

          <article
            className="stat-card"
            key={title}
          >

            <div className={`stat-icon ${color}`}>
              <Icon size={23} />
            </div>

            <div className="stat-info">
              <p>{title}</p>
              <h2>{formatNumber(value)}</h2>
            </div>

            <div className="stat-decoration"></div>

          </article>

        ))}

      </section>


      {/* MONITORING + SYSTEM STATUS */}

      <section className="monitoring-grid">


        {/* LIVE VIDEO FEED */}

        <article className="panel feed-panel">

          <div className="panel-header">

            <div>
              <h2>Live Traffic Monitoring</h2>
              <p>
                YOLO AI Vehicle Detection Interface
              </p>
            </div>


            <div className="detection-controls">

              <button
                className="start-detection-btn"
                onClick={startDetection}
                disabled={
                  detectionLoading ||
                  detectionStatus === "running" ||
                  detectionStatus === "starting"
                }
              >
                {detectionLoading
                  ? "Please wait..."
                  : "Start Detection"}
              </button>


              <button
                className="stop-detection-btn"
                onClick={stopDetection}
                disabled={
                  detectionLoading ||
                  detectionStatus !== "running"
                }
              >
                Stop Detection
              </button>

            </div>

          </div>


          {/* VIDEO CONTAINER */}

          <div className="video-feed">


            {/* LIVE YOLO STREAM */}

            {detectionStatus !== "stopped" &&
              detectionStatus !== "error" && (

                <img
                  className="traffic-video"
                  src={`${API}/detection/stream`}
                  alt="Live YOLO vehicle detection stream"

                  onLoad={() => {
                    setVideoReady(true);
                    setVideoError(false);
                  }}

                  onError={() => {
                    setVideoReady(false);
                    setVideoError(true);
                  }}
                />

              )}


            {/* VIDEO DECORATIONS */}

            <div className="feed-grid"></div>
            <div className="feed-scanline"></div>

            <div className="feed-corner top-left"></div>
            <div className="feed-corner top-right"></div>
            <div className="feed-corner bottom-left"></div>
            <div className="feed-corner bottom-right"></div>


            {/* TOP OVERLAY */}

            <div className="feed-top-overlay">

              <span className="camera-label">
                <Camera size={15} />
                CAM-01
              </span>

              <span className="feed-time">
                {new Date().toLocaleTimeString()}
              </span>

            </div>


            {/* PLACEHOLDER */}

            {!videoReady && (

              <div className="feed-placeholder">

                <div className="feed-placeholder-icon">
                  <Camera size={32} />
                </div>


                <h3>

                  {detectionStatus === "error"
                    ? "Detection Error"
                    : detectionStatus === "stopped"
                      ? "Detection Not Started"
                      : videoError
                        ? "Stream Not Available"
                        : "Waiting for Detection Stream"}

                </h3>


                <p>

                  {detectionStatus === "stopped"
                    ? "Click Start Detection to begin YOLO vehicle monitoring."
                    : detectionStatus === "error"
                      ? detectionStats.message ||
                        "Check the backend terminal for details."
                      : "Loading annotated vehicle detection frames..."}

                </p>


                <span className="feed-placeholder-tag">
                  {detectionStatus.toUpperCase()}
                </span>

              </div>

            )}


            {/* BOTTOM OVERLAY */}

            <div className="feed-bottom-overlay">

              <div>
                <CircleDot size={13} />

                {detectionStatus === "running"
                  ? "AI DETECTION RUNNING"
                  : detectionStatus === "starting"
                    ? "STARTING DETECTION"
                    : "DETECTION STOPPED"}

              </div>

              <span>AI MONITORING</span>

            </div>

          </div>


          {/* FEED INFORMATION */}

          <div className="feed-info-row">

            <div className="feed-info-item">
              <span className="feed-info-label">
                CAMERA
              </span>
              <strong>Camera 01</strong>
            </div>


            <div className="feed-info-item">

              <span className="feed-info-label">
                STATUS
              </span>

              <strong
                className={
                  videoReady
                    ? "status-green"
                    : "status-red"
                }
              >

                {videoReady
                  ? "AI Stream Playing"
                  : detectionStatus === "running"
                    ? "Connecting..."
                    : detectionStatus === "error"
                      ? "Detection Error"
                      : "Stopped"}

              </strong>

            </div>


            <div className="feed-info-item">
              <span className="feed-info-label">
                EVENTS
              </span>

              <strong>
                {formatNumber(recent.length)}
              </strong>
            </div>

          </div>


          {/* LIVE COUNTS */}

          <div className="live-counts">

            <div>
              <span>Currently Visible</span>

              <strong>
                {formatNumber(
                  detectionStats.active_vehicles
                )}
              </strong>
            </div>


            <div>
              <span>Unique Vehicles</span>

              <strong>
                {formatNumber(
                  detectionStats.total_vehicles
                )}
              </strong>
            </div>


            <div>
              <span>Line Crossings</span>

              <strong>
                {formatNumber(
                  detectionStats.total_crossings
                )}
              </strong>
            </div>

          </div>

        </article>


        {/* DETECTION STATUS */}

        <article className="panel system-panel">

          <div className="panel-header">

            <div>
              <h2>Detection Status</h2>
              <p>System monitoring information</p>
            </div>

            <ShieldCheck
              size={23}
              className="shield-icon"
            />

          </div>


          {/* API CONNECTION */}

          <div className="system-status-card">

            <div
              className={`system-status-icon ${
                connected ? "online" : "offline"
              }`}
            >
              <Server size={25} />
            </div>

            <div>
              <span className="system-label">
                API CONNECTION
              </span>

              <h3>
                {connected
                  ? "Connected"
                  : "Disconnected"}
              </h3>
            </div>

            <span
              className={`status-pill ${
                connected
                  ? "pill-online"
                  : "pill-offline"
              }`}
            >
              {connected ? "ONLINE" : "OFFLINE"}
            </span>

          </div>


          {/* ANALYTICS */}

          <div className="system-status-card">

            <div className="system-status-icon detection">
              <Eye size={25} />
            </div>

            <div>
              <span className="system-label">
                ANALYTICS DATA
              </span>

              <h3>
                {connected
                  ? "Available"
                  : "Unavailable"}
              </h3>
            </div>

            <span
              className={`status-pill ${
                connected
                  ? "pill-online"
                  : "pill-offline"
              }`}
            >
              {connected ? "READY" : "WAITING"}
            </span>

          </div>


          {/* DETECTOR STATUS */}

          <div className="system-status-card">

            <div className="system-status-icon monitor">
              <Radio size={25} />
            </div>

            <div>
              <span className="system-label">
                YOLO DETECTION
              </span>

              <h3>
                {detectionStatus === "running"
                  ? "Running"
                  : detectionStatus === "starting"
                    ? "Starting"
                    : detectionStatus === "error"
                      ? "Error"
                      : "Stopped"}
              </h3>
            </div>

            <span
              className={`status-pill ${
                detectionStatus === "running"
                  ? "pill-online"
                  : "pill-active"
              }`}
            >
              {detectionStatus.toUpperCase()}
            </span>

          </div>


          {/* AUTO REFRESH */}

          <div className="system-status-card">

            <div className="system-status-icon performance">
              <Gauge size={25} />
            </div>

            <div>
              <span className="system-label">
                AUTO REFRESH
              </span>

              <h3>5 Seconds</h3>
            </div>

            <span className="status-pill pill-active">
              ACTIVE
            </span>

          </div>


          {/* RECENT EVENTS */}

          <div className="system-status-card">

            <div className="system-status-icon monitor">
              <Activity size={25} />
            </div>

            <div>
              <span className="system-label">
                RECENT EVENTS
              </span>

              <h3>
                {formatNumber(recent.length)} Records
              </h3>
            </div>

          </div>


          <div className="system-footer">

            <ShieldCheck size={16} />

            <span>
              {connected
                ? "Dashboard API responses verified"
                : "Waiting for successful API responses"}
            </span>

          </div>

        </article>

      </section>


      {/* DIRECTION ANALYTICS */}

      <section className="direction-panel panel">

        <div className="panel-header">

          <div>
            <h2>Vehicle Direction Analytics</h2>
            <p>
              Crossing distribution by recorded direction
            </p>
          </div>

          <span className="chart-badge">
            RECENT EVENTS
          </span>

        </div>


        {directionData.length > 0 ? (

          <div className="direction-grid">

            {directionData.map((item, index) => {

              const Icon =
                directionIcons[
                  index % directionIcons.length
                ];

              const colorClass =
                directionColors[
                  index % directionColors.length
                ];

              const percentage = recent.length
                ? (item.count / recent.length) * 100
                : 0;


              return (

                <div
                  className="direction-card"
                  key={item.direction}
                >

                  <div
                    className={`direction-icon ${colorClass}`}
                  >
                    <Icon size={23} />
                  </div>


                  <div className="direction-main">

                    <div className="direction-heading">

                      <h3>{item.direction}</h3>

                      <strong>
                        {formatNumber(item.count)}
                      </strong>

                    </div>


                    <div className="direction-track">

                      <div
                        className={`direction-progress ${colorClass}`}
                        style={{
                          width: `${percentage}%`
                        }}
                      ></div>

                    </div>


                    <span className="direction-percent">
                      {percentage.toFixed(1)}% of recent events
                    </span>

                  </div>

                </div>

              );

            })}

          </div>

        ) : (

          <div className="direction-empty">

            <ArrowLeftRight size={30} />

            <p>No direction data available yet.</p>

            <span>
              Direction analytics will appear when crossing events are recorded.
            </span>

          </div>

        )}

      </section>


      {/* CHARTS */}

      <section className="charts">


        {/* VEHICLE TYPE CHART */}

        <article className="panel">

          <div className="panel-header">

            <div>
              <h2>Vehicle Type Distribution</h2>
              <p>
                Breakdown of detected vehicle categories
              </p>
            </div>

            <span className="chart-badge">
              STATISTICS
            </span>

          </div>


          <div className="chart-container">

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <BarChart
                data={types}
                margin={{
                  top: 15,
                  right: 10,
                  left: -15,
                  bottom: 5
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#263244"
                />


                <XAxis
                  dataKey="type"
                  tick={{
                    fill: "#94a3b8",
                    fontSize: 12
                  }}
                  axisLine={{
                    stroke: "#334155"
                  }}
                  tickLine={false}
                />


                <YAxis
                  allowDecimals={false}
                  tick={{
                    fill: "#94a3b8",
                    fontSize: 12
                  }}
                  axisLine={false}
                  tickLine={false}
                />


                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: "12px",
                    color: "#f8fafc"
                  }}
                  cursor={{
                    fill: "rgba(96,165,250,0.08)"
                  }}
                />


                <Bar
                  dataKey="count"
                  name="Vehicles"
                  fill="#60a5fa"
                  radius={[8, 8, 0, 0]}
                  maxBarSize={60}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </article>


        {/* VEHICLE COLOUR CHART */}

        <article className="panel">

          <div className="panel-header">

            <div>
              <h2>Vehicle Colour Distribution</h2>
              <p>
                Detected vehicles grouped by colour
              </p>
            </div>

            <span className="chart-badge">
              STATISTICS
            </span>

          </div>


          <div className="chart-container">

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <PieChart>

                <Pie
                  data={colors}
                  dataKey="count"
                  nameKey="color"
                  cx="50%"
                  cy="45%"
                  outerRadius={100}
                  innerRadius={55}
                  paddingAngle={3}
                  label={({ color, percent }) =>
                    `${color} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={{
                    stroke: "#64748b"
                  }}
                >

                  {colors.map((entry, index) => (

                    <Cell
                      key={index}
                      fill={COLORS[index % COLORS.length]}
                      stroke="none"
                    />

                  ))}

                </Pie>


                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: "12px",
                    color: "#f8fafc"
                  }}
                />


                <Legend
                  wrapperStyle={{
                    color: "#cbd5e1",
                    fontSize: "12px"
                  }}
                />

              </PieChart>

            </ResponsiveContainer>

          </div>

        </article>

      </section>


      {/* RECENT EVENTS TABLE */}

      <section className="panel recent">

        <div className="panel-header recent-header">

          <div>
            <h2>Recent Vehicle Crossing Events</h2>
            <p>
              Latest recorded vehicle crossing activity
            </p>
          </div>

          <span className="event-count">
            {recent.length} Events
          </span>

        </div>


        <div className="table-wrap">

          <table>

            <thead>

              <tr>
                <th>Vehicle ID</th>
                <th>Type</th>
                <th>Colour</th>
                <th>Direction</th>
                <th>Timestamp</th>
              </tr>

            </thead>


            <tbody>

              {recent.map((item, index) => (

                <tr key={item.event_id ?? index}>

                  <td>
                    <span className="vehicle-id">
                      {item.vehicle_id}
                    </span>
                  </td>


                  <td>
                    <span className="type-badge">
                      {item.vehicle_type}
                    </span>
                  </td>


                  <td>

                    <span className="color-value">

                      <span
                        className="color-dot"
                        style={{
                          background:
                            item.vehicle_color?.toLowerCase() ||
                            "#64748b"
                        }}
                      ></span>

                      {item.vehicle_color}

                    </span>

                  </td>


                  <td>
                    <span className="direction-badge">
                      {item.direction}
                    </span>
                  </td>


                  <td className="timestamp">
                    {item.timestamp}
                  </td>

                </tr>

              ))}


              {recent.length === 0 && (

                <tr>
                  <td
                    colSpan="5"
                    className="empty-state"
                  >
                    No crossing events found.
                  </td>
                </tr>

              )}

            </tbody>

          </table>

        </div>

      </section>


      {/* FOOTER */}

      <footer className="dashboard-footer">

        <div>
          <span className="footer-dot"></span>
          Vehicle Analytics System
        </div>

        <p>
          AI-Powered Traffic Monitoring & Analytics
        </p>

      </footer>

    </main>

  );

}

export default App;
