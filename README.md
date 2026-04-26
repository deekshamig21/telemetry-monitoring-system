# Telemetry, Logging, and Real-Time Monitoring System

## Overview

This project simulates a simplified aerospace telemetry system for a rocket hopper. It generates dummy flight data, streams it to a ground station, logs it reliably, and visualizes key parameters in real time.

The goal is to demonstrate system design thinking, handling of real-time data, and separation of concerns across components.

---

## System Architecture

The system is divided into two main parts:

### 1. Vehicle Side (Simulator)

* Generates telemetry data at ~50–100 Hz
* Parameters:

  * Timestamp
  * Altitude
  * Vertical Velocity
  * Acceleration
  * Orientation (Pitch, Roll, Yaw)

### 2. Ground Station

* Receives telemetry data
* Logs data to a CSV file
* Displays real-time plots

### Data Flow

Vehicle Simulator → (Data Stream) → Ground Station → (Logging + Visualization)

---

## Features

* Real-time telemetry simulation
* Continuous data streaming
* Live visualization (Altitude, Velocity, Orientation)
* Persistent logging to CSV
* Modular structure for scalability

---

## Tech Stack

* Python
* Matplotlib (real-time visualization)
* CSV (data logging)

---

## How to Run

### 1. Install dependencies

```bash
pip install matplotlib
```

### 2. Run the system

```bash
python run_telemetry_dashboard.py
```

---

## Output

### Live Dashboard

* Real-time updating plots for:

  * Altitude
  * Velocity
  * Orientation (Pitch)

### Logged Data

* File: `telemetry_log.csv`
* Contains timestamped telemetry data for post-analysis

---

## Design Decisions

### 1. CSV Logging

* Chosen for simplicity and readability
* Easy to inspect and debug
* Trade-off: Not optimal for very high data rates compared to binary formats

### 2. Matplotlib for Visualization

* Quick to implement and widely supported
* Suitable for prototyping real-time systems
* Trade-off: Limited scalability compared to web-based dashboards

### 3. Single-Process Demo Version

* Simplifies execution and debugging
* Combines simulation, logging, and visualization
* Trade-off: Not fully representative of distributed systems

---

## Handling Real-Time Constraints

* Data generated at fixed intervals (~50–100 Hz)
* Continuous loop ensures steady updates
* Logging happens alongside visualization without blocking execution

---

## Limitations

* No real network communication (in demo version)
* No packet loss or latency simulation
* Limited scalability for high-frequency or large datasets
* Basic visualization only

---

## Future Improvements

* Add UDP/TCP communication layer
* Simulate packet loss and network latency
* Implement asynchronous or buffered logging
* Replace matplotlib with a web dashboard (e.g., Streamlit or Dash)
* Add replay system for logged data
* Introduce configuration files (YAML/JSON)

---

## Demo

(Add a screenshot here)

---

## Key Takeaways

* Designed a modular telemetry pipeline
* Worked with real-time data generation and visualization
* Implemented continuous logging without interrupting execution
* Considered real-world system constraints and trade-offs
