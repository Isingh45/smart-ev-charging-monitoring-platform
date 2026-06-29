# Smart EV Charging Monitoring Platform

## Overview
Cloud-inspired EV charging monitoring system that simulates distributed charging stations and visualizes real-time telemetry data through a web dashboard.

## Technologies
* React
* Python
* Docker
* Containernet
* Bash
* JSON Server

## Architecture
EV Stations (Docker + Containernet) -> Telemetry Generation (Python) -> Synchronization Pipeline (Bash) -> JSON Storage -> REST API (json-server) -> React Dashboard

## Features
* Real-time telemetry monitoring
* Battery and voltage tracking
* Station recommendation logic
* Live voltage trend visualization
* Distributed edge-node simulation

## Repository Structure
* docs/ — Final project report and presentation
* source_code/ — Smart EV simulation, pipeline, API integration, and React dashboard

## How to Run

### 1. Prerequisites
Ensure the following are installed on an Ubuntu Linux environment:
* Containernet (SDN Framework)
* Docker and Node.js
* Global API Tool: sudo npm install -g json-server

### 2. Execution Steps

* Step 1: Start the Topology
  sudo python3 ~/smart_ev_lab/smart_ev_sim.py

* Step 2: Initialize Telemetry (Run inside containernet> prompt)
  * Station 1:
    station1 python3 -c "import time, json, random; f=open('/ev_sim_cloud_log.json','a'); [f.write(json.dumps({'station_id':'STN-001', 'battery_pct':round(random.uniform(60,95),1), 'voltage_v':round(random.uniform(230, 245), 2)})+'\n') or f.flush() or time.sleep(2) for _ in range(1000)]" &
  * Station 2:
    station2 python3 -c "import time, json, random; f=open('/ev_sim_cloud_log.json','a'); [f.write(json.dumps({'station_id':'STN-002', 'battery_pct':round(random.uniform(20,60),1), 'voltage_v':round(random.uniform(230, 245), 2)})+'\n') or f.flush() or time.sleep(2) for _ in range(1000)]" &

* Step 3: Launch API Bridge (New Terminal)
  json-server --watch ~/smart_ev_lab/ev_sim_cloud_log.json --port 5000

* Step 4: Start Sync Pipeline (New Terminal)
  while true; do sudo docker cp mn.station1:/ev_sim_cloud_log.json ~/smart_ev_lab/stn1.json 2>/dev/null; sudo docker cp mn.station2:/ev_sim_cloud_log.json ~/smart_ev_lab/stn2.json 2>/dev/null; echo '{"telemetry": [' > ~/smart_ev_lab/temp_log.json; { tail -n 15 ~/smart_ev_lab/stn1.json 2>/dev/null; tail -n 15 ~/smart_ev_lab/stn2.json 2>/dev/null; } | grep "{" | paste -sd, - >> ~/smart_ev_lab/temp_log.json; echo ']}' >> ~/smart_ev_lab/temp_log.json; mv ~/smart_ev_lab/temp_log.json ~/smart_ev_lab/ev_sim_cloud_log.json; sleep 2; done

* Step 5: Launch Dashboard (New Terminal)
  cd ~/smart_ev_lab/ev-dashboard && npm install && npm start

## What I Learned
* Managing application state in client-side JavaScript and polling telemetry datasets asynchronously.
* Building decoupled pipelines to handle multi-node concurrency conflicts and file-locking issues.
* Emulating network infrastructure topologies locally using containerization frameworks.

## Future Improvements
* Search functionality
* Improved UI/UX styling
* Optional backend integration

---
**Authors:** Inderpal Singh & Sukhpinder Singh  
**Course:** CS 623 Cloud Computing — California State University, East Bay (Spring 2026)
