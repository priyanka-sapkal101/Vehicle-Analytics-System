
import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import {
  Car, Bus, Truck, Bike, Activity, RefreshCw
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [summary, setSummary] = useState({});
  const [colors, setColors] = useState([]);
  const [types, setTypes] = useState([]);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    try {
      setError("");

      const [s, c, t, r] = await Promise.all([
        fetch(`${API}/analytics/summary`),
        fetch(`${API}/analytics/colors`),
        fetch(`${API}/analytics/types`),
        fetch(`${API}/analytics/recent`)
      ]);

      if (![s, c, t, r].every(response => response.ok)) {
        throw new Error("Could not load dashboard data.");
      }

      const [summaryData, colorData, typeData, recentData] =
        await Promise.all([
          s.json(), c.json(), t.json(), r.json()
        ]);

      setSummary(summaryData);
      setColors(colorData.colors || []);
      setTypes(typeData.vehicle_types || []);
      setRecent(recentData.recent_events || []);
    } catch (err) {
      setError(err.message + " Make sure FastAPI is running.");
    }
  };

  useEffect(() => {
    loadDashboard();
    const timer = setInterval(loadDashboard, 5000);
    return () => clearInterval(timer);
  }, []);

  const cards = [
    { title: "Total Vehicles", value: summary.total_vehicles ?? 0, icon: Car },
    { title: "Total Crossings", value: summary.total_crossings ?? 0, icon: Activity },
    { title: "Cars", value: summary.cars ?? 0, icon: Car },
    { title: "Buses", value: summary.buses ?? 0, icon: Bus },
    { title: "Trucks", value: summary.trucks ?? 0, icon: Truck },
    { title: "Motorcycles", value: summary.motorcycles ?? 0, icon: Bike }
  ];

  const COLORS = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444",
                  "#8b5cf6", "#64748b", "#ec4899", "#14b8a6"];

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <h1>Vehicle Analytics Dashboard</h1>
          <p>Real-Time Vehicle Monitoring System</p>
        </div>
        <button onClick={loadDashboard} className="refresh">
          <RefreshCw size={18} /> Refresh
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="stats">
        {cards.map(({ title, value, icon: Icon }) => (
          <article className="stat-card" key={title}>
            <Icon size={27} />
            <p>{title}</p>
            <h2>{value}</h2>
          </article>
        ))}
      </section>

      <section className="charts">
        <article className="panel">
          <h2>Vehicle Type Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={types}>
  <XAxis dataKey="type" />
  <YAxis allowDecimals={false} />
  <Tooltip />
  <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
</BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <h2>Vehicle Colour Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
  data={colors}
  dataKey="count"
  nameKey="color"
  cx="50%"
  cy="45%"
  outerRadius={95}
  label
>
  {colors.map((entry, index) => (
    <Cell key={index} fill={COLORS[index % COLORS.length]} />
  ))}
</Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section className="panel recent">
        <h2>Recent Vehicle Crossing Events</h2>
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
                  <td>{item.vehicle_id}</td>
                  <td>{item.vehicle_type}</td>
                  <td>{item.vehicle_color}</td>
                  <td>{item.direction}</td>
                  <td>{item.timestamp}</td>
                </tr>
              ))}
              {recent.length === 0 && (
                <tr><td colSpan="5">No crossing events found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default App;
