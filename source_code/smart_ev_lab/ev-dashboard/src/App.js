import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

const App = () => {
  const [data, setData] = useState([]);
  const [stations, setStations] = useState({});

  const getBestStation = (stationsObj) => {
    const stationsArray = Object.values(stationsObj);
    if (stationsArray.length === 0) return null;

    return stationsArray.reduce((best, current) => {
      const scoreBest = best.battery_pct + best.voltage_v;
      const scoreCurrent = current.battery_pct + current.voltage_v;
      return scoreCurrent > scoreBest ? current : best;
    });
  };

  const getAvailability = (battery, voltage) => {
    if (battery < 20) return "Unavailable";
    if (voltage < 235) return "Busy";
    return "Available";
  };

  const getAvailabilityColor = (battery, voltage) => {
    if (battery < 20) return "#e74c3c";
    if (voltage < 235) return "#f39c12";
    return "#2ecc71";
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:5000/telemetry");

        const logs = (response.data || []).map((item, index) => ({
          ...item,
          timestamp: index
        }));

        let latestStatus = {};

        if (logs.length > 0) {
          setData(logs);

          logs.forEach((log) => {
            latestStatus[log.station_id] = log;
          });
        }

        setStations(latestStatus);
      } catch (err) {
        console.error("Error fetching simulation data:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const bestStation = getBestStation(stations);

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>⚡ Smart EV Charging Dashboard</h1>

      {bestStation && (
        <h2 style={{ color: "green" }}>
          ⭐ Recommended Station: {bestStation.station_id}
        </h2>
      )}

      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        {Object.keys(stations).map((sid) => {
          const station = stations[sid];
          const status = getAvailability(
            station.battery_pct,
            station.voltage_v
          );

          return (
            <div
              key={sid}
              style={{
                border: "1px solid #ddd",
                borderRadius: "10px",
                padding: "20px",
                width: "200px"
              }}
            >
              <h3>{sid}</h3>

              <p>
                <strong>Status:</strong>{" "}
                <span
                  style={{
                    color: getAvailabilityColor(
                      station.battery_pct,
                      station.voltage_v
                    )
                  }}
                >
                  {status}
                </span>
              </p>

              <h2>{parseFloat(station.battery_pct).toFixed(1)}%</h2>

              {/* Battery Bar */}
              <div
                style={{
                  height: "10px",
                  background: "#eee",
                  borderRadius: "5px",
                  overflow: "hidden"
                }}
              >
                <div
                  style={{
                    width: `${station.battery_pct}%`,
                    height: "100%",
                    background: getAvailabilityColor(
                      station.battery_pct,
                      station.voltage_v
                    )
                  }}
                />
              </div>

              <p style={{ marginTop: "10px" }}>
                Voltage: {parseFloat(station.voltage_v).toFixed(2)}V
              </p>
            </div>
          );
        })}
      </div>

      {/* GRAPH */}
      <div style={{ marginTop: "40px", height: "300px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />

            {/* 🔥 FIXED LINE (NO MORE WOBBLE) */}
            <Line
              type="linear"
              dataKey="voltage_v"
              stroke="#3498db"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default App;
