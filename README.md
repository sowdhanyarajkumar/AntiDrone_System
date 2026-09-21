# Aeronex: High Altitude Performance Optimization & Robust Design of Anti-Drone System

[![DRDO](https://img.shields.io/badge/Organization-DRDO-blue.svg)](https://drdo.gov.in)
[![SIH](https://img.shields.io/badge/Problem%20Statement-26050-orange.svg)](https://sih.gov.in)
[![Category](https://img.shields.io/badge/Category-Robotics%20%26%20Drones-emerald.svg)]()
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-009688.svg)]()
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Tailwind%20%2B%20Vite-61DAFB.svg)]()

> **SIH Problem Statement ID: 26050**  
> **Title:** High Altitude Performance Optimization and Robust Design of Anti-Drone System  
> **Organization:** Defence Research and Development Organisation (DRDO)  
> **Category:** Hardware / Robotics and Drones  
> **Software Scope:** Pure Software Prototype (No physical hardware or communication required for execution).

---

## 📌 Project Overview

At high altitudes (3,000m to 6,000m AMSL, such as in the Himalayas, Ladakh, or Siachen sectors), anti-drone defense platforms face severe physical degradation:
1. **Rarefied Atmosphere:** Atmospheric density and barometric pressure drop by up to 45-50%, severely reducing convective heat dissipation over heatsinks and cooling fans.
2. **Thermal Throttling:** Electronic components and AI compute accelerators reach higher steady-state core temperatures, triggering hardware clock throttling, increasing AI model inference latency, and dropping camera frame rates (FPS).
3. **Mechanical Resonance:** Wind buffeting and platform vibration induce optical jitter, reducing tracking crosshair lock stability and confidence.

**Aeronex** is an end-to-end engineering prototype demonstrating this coupled chain of physical-compute phenomena in real time with an actual physics simulation engine, live computer vision detection (YOLOv8 + OpenCV), software pan/tilt servo tracking, a rule-based health engine, persistent SQLite telemetry, and a dark tactical engineering dashboard.

---

## 🚀 Key Features

* **Physics-Informed Atmospheric Simulation:** Realistic barometric pressure, lapse-rate ambient temperature, normalized air density indicator, and convective cooling capacity across 0m to 6,000m elevation.
* **Coupled Compute & Thermal Modeling:** Higher simulated CPU utilization and reduced cooling capacity increase core junction temperatures, simulating thermal throttling with elevated inference latency and reduced FPS.
* **Dual AI Detection Engine:**
  * **Live AI Mode:** Uses real webcams or video files with OpenCV and Ultralytics YOLOv8 nano.
  * **Simulated AI Mode:** High-fidelity synthetic boresight generator when no camera is attached.
  * *Notice: "Prototype AI model — specialized drone training required for deployment."*
* **Software Optical Tracking:** Computes boresight target displacement errors ($\Delta X, \Delta Y$) and maps them to simulated dual-axis pan and tilt servo angles ($0^\circ$ to $180^\circ$).
* **Multidimensional System Health Engine:** Dynamically assesses physical, thermal, compute, and tracking health with explicit diagnostic reason strings (e.g. `NORMAL`, `WARNING`, `DEGRADED`, `CRITICAL`).
* **Session Lifecycle Management:** Unique session IDs (`HA-2026-XXXX`), start/pause/resume/stop states, and zero synthetic startup data.
* **Persistent SQLite Database:** Stores all telemetry, computer metrics, detections, tracking records, and system events.
* **One-Click CSV Export:** Generates consolidated mission telemetry and tracking CSV reports directly from SQLite.
* **WebSocket Real-Time Broadcast:** High-frequency binary/JSON state broadcast over `/ws/telemetry` with automatic client reconnection.
* **Parametric High-Altitude Analysis:** Detailed comparative matrix and graphs comparing baseline (1,000m) vs extreme high-altitude (5,000m) conditions.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────┐
                    │    SIMULATION ENGINE    │
                    │  (Altitude, Pressure,   │
                    │   Cooling, Throttling)  │
                    └───────────┬─────────────┘
                                │ (1.0 Hz Tick)
                                ▼
                    ┌─────────────────────────┐
                    │     FASTAPI BACKEND     │
                    │  • Simulation Service   │
                    │  • Health Engine        │
                    │  • AI / Tracking Engine │
                    └───────────┬─────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          ┌──────────────┐              ┌──────────────┐
          │  SQLite DB   │              │  WEBSOCKET   │
          │(data/sys.db) │              │/ws/telemetry │
          └──────────────┘              └──────┬───────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │ REACT FRONTEND  │
                                      │ (Vite/Tailwind) │
                                      │ 10 HUD Views    │
                                      └─────────────────┘
```

---

## 💻 Quick Start Guide

### Prerequisites
* Windows 10/11 or Linux / macOS
* Python 3.10 (recommended for PyTorch/OpenCV prebuilt wheels)
* Node.js v18+ and npm

### 1. Launch All (One-Click on Windows)
Simply double-click:
```bat
run_all.bat
```
This starts both the FastAPI backend server (port 8000) and the Vite frontend dev server (port 5173).

---

### 2. Manual Startup

#### Backend Setup
```powershell
# 1. Create and activate Python 3.10 virtual environment
py -3.10 -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```
* Backend API: `http://localhost:8000`
* Interactive OpenAPI Documentation: `http://localhost:8000/docs`

#### Frontend Setup
```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite dev server
npm run dev
```
* Frontend Dashboard: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the full backend pytest test suite covering altitude physics, database schemas, health thresholds, tracking solver, and REST endpoints:
```powershell
.venv\Scripts\pytest backend/tests -v
```

---

## 📖 Complete Documentation Index

* [System Architecture](docs/architecture.md)
* [Atmospheric Simulation Model](docs/simulation.md)
* [Database Design & Schema](docs/database.md)
* [AI Detection & Tracking Pipeline](docs/ai.md)
* [REST API & WebSocket Specifications](docs/api.md)
* [Step-by-Step Demonstration Script](docs/demo.md)

---

## ⚖️ Safety & Scope Disclaimer

This software is an engineering research prototype designed for performance simulation, academic demonstration, and algorithmic verification. It contains no weapon systems, no radio frequency jamming capabilities, and no autonomous neutralization logic.
