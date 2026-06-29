# Smart EV Charging Monitoring Platform

## Overview

A cloud-inspired EV charging monitoring platform that simulates a distributed charging infrastructure using Containernet and Docker. The system generates real-time telemetry from multiple virtual EV charging stations, synchronizes telemetry through a custom data pipeline, exposes the data through a REST API, and visualizes live system status using a React dashboard.

The project demonstrates cloud computing concepts through a local cloud simulation by integrating distributed edge nodes, centralized data synchronization, API services, and real-time web-based visualization.

---

# Technologies

* React
* Python
* Docker
* Containernet (Software-Defined Networking)
* Bash
* JSON
* JSON Server

---

# Architecture

```
Docker EV Stations (Containernet)
            │
            ▼
Python Telemetry Generation
            │
            ▼
Bash Synchronization Pipeline
            │
            ▼
Central JSON Storage
            │
            ▼
REST API (json-server)
            │
            ▼
React Dashboard
```

---

# Features

* **Distributed EV Station Simulation:** Simulates multiple EV charging stations using Docker containers connected through a Containernet software-defined network.

* **Real-Time Telemetry Generation:** Generates simulated battery percentage, voltage, current, and charging status for each virtual charging station using Python.

* **Telemetry Synchronization Pipeline:** Uses a custom Bash pipeline to continuously collect telemetry from multiple Docker containers, merge the latest records, and maintain a centralized JSON data source.

* **REST API Integration:** Exposes synchronized telemetry through JSON Server, allowing the frontend to retrieve live station data using standard HTTP requests.

* **Live Monitoring Dashboard:** Displays battery percentage, voltage, station availability, and recommended charging station through a React-based dashboard.

* **Real-Time Voltage Visualization:** Continuously updates a time-series voltage graph using Recharts to visualize charging station telemetry.

* **Station Recommendation Logic:** Evaluates live battery and voltage metrics to recommend the most suitable charging station.

---

# Repository Structure

```
docs/
    Final Project Report
    Final Presentation

source_code/
    smart_ev_lab/
        smart_ev_sim.py
        run_pipeline.sh
        ev-dashboard/
```

---

# How to Run

## Prerequisites

Install the following on Ubuntu Linux:

* Containernet
* Docker
* Node.js
* JSON Server

```
sudo npm install -g json-server
```

---

## Execution Steps

### 1. Launch the EV Network Simulation

```
sudo python3 smart_ev_sim.py
```

### 2. Generate Telemetry

Run the provided telemetry commands inside the Containernet CLI for each virtual charging station.

### 3. Start the REST API

```
json-server --watch ~/smart_ev_lab/ev_sim_cloud_log.json --port 5000
```

### 4. Start the Synchronization Pipeline

```
bash run_pipeline.sh
```

### 5. Launch the React Dashboard

```
cd ev-dashboard
npm install
npm start
```

---

# What I Learned

* Designing distributed system architectures using Docker and Containernet.
* Building real-time telemetry pipelines using Python, Bash, and JSON.
* Integrating REST APIs with React applications for live data visualization.
* Managing asynchronous client-side state updates through periodic polling.
* Developing modular software components that separate simulation, data synchronization, API services, and frontend visualization.

---

# Future Improvements

* Replace the local JSON-based API with a cloud-hosted backend such as AWS or Google Cloud.
* Implement persistent database storage for long-term telemetry retention.
* Add user authentication and charging station reservation capabilities.
* Expand the simulation to support additional charging stations and larger network topologies.

---

# Authors

**Inderpal Singh**

**Sukhpinder Singh**

California State University, East Bay

CS 623 – Cloud Computing

Spring 2026
