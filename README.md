# AeroNexGp: High-Altitude Performance Optimization & Robust Anti-Drone Platform

[![Live Deployment](https://img.shields.io/badge/Live%20Demo-Railway-00f0ff.svg?style=for-the-badge&logo=railway)](https://aeronex-gp-production.up.railway.app)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite%20%2B%20Tailwind-61DAFB.svg?style=for-the-badge&logo=react)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.10-3776AB.svg?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)]()

> 🌐 **Live Application:** [https://aeronex-gp-production.up.railway.app](https://aeronex-gp-production.up.railway.app)  
> 📦 **GitHub Repository:** [https://github.com/sowdhanyarajkumar/AntiDrone_System](https://github.com/sowdhanyarajkumar/AntiDrone_System)

---

## 📌 Overview

At high altitudes (3,000 m to 6,000 m AMSL, such as in mountainous defense frontiers):
1. **Rarefied Atmosphere:** Barometric pressure drops by 45–50%, reducing air density and degrading natural/forced convective heatsink cooling.
2. **Thermal Throttling:** Onboard compute modules and AI accelerators overheat faster under sustained load, triggering hardware throttling, dropping camera frame rates (FPS), and increasing AI inference latency.
3. **Mechanical Perturbations & Buffeting:** Strong gusts and mechanical vibrations induce optical jitter, degrading target tracking lock and crosshair stability.

**AeroNexGp** is a full-stack, cloud-ready anti-drone performance simulation, tracking, and telemetry platform. It couples atmospheric physics equations, real-time AI computer vision (YOLOv8 + OpenCV), dual-axis servo tracking calculations, and dynamic health assessment into a unified tactical engineering dashboard.

---

## 🚀 Key Features

* **Real-Time Physics Engine (0–6,000 m):** Models barometric pressure lapse rate, air density ratio ($\rho / \rho_0$), ambient temperature, and convective cooling efficiency.
* **Coupled Compute & Thermal Model:** Simulates CPU/GPU junction temperatures based on compute load, vibration stress, and atmospheric cooling limits.
* **Dual AI Detection Pipeline:**
  * **Live AI Mode:** Uses connected camera feeds or video streams with Ultralytics YOLOv8 inference and OpenCV.
  * **Simulated AI Mode:** Realistic synthetic drone trajectory and boresight detection when hardware cameras are absent.
* **Target Tracking & Servo Solver:** Calculates optical boresight target displacement errors ($\Delta X, \Delta Y$) and computes dual-axis pan/tilt gimbal angles ($0^\circ$ to $180^\circ$).
* **System Health Assessment:** Monitors physical, compute, thermal, and tracking states to generate real-time diagnostic alerts (`NORMAL`, `WARNING`, `DEGRADED`, `CRITICAL`).
* **Session Lifecycle & Data Export:** Start, pause, resume, and archive telemetry sessions with unique session IDs and one-click consolidated CSV downloads.
* **Bidirectional WebSocket Broker:** Streams telemetry packets and disturbance updates at 1 Hz with automatic reconnect.
* **Fully Responsive Tactical UI:** Mobile drawer navigation, adaptive metric grids, dynamic HUD glow themes, and parametric high-altitude analysis charts.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PHYSICAL ENVIRONMENT                    │
│      Altitude (0-6000m) • Pressure • Air Density • Temp     │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Atmospheric Physics)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  AERONEXGP BACKEND (FastAPI)                │
│                                                             │
│   ┌────────────────────┐          ┌─────────────────────┐   │
│   │ Simulation Service │          │ System Health Engine│   │
│   └─────────┬──────────┘          └──────────┬──────────┘   │
│             │                                │              │
│   ┌─────────▼──────────┐          ┌──────────▼──────────┐   │
│   │ AI Vision (YOLOv8) │          │ Tracking Controller │   │
│   └─────────┬──────────┘          └──────────┬──────────┘   │
│             └────────────────┬───────────────┘              │
│                              │                              │
│               ┌──────────────┴──────────────┐               │
│               ▼                             ▼               │
│        ┌──────────────┐              ┌──────────────┐       │
│        │  SQLite DB   │              │  WEBSOCKET   │       │
│        │ (data/sys.db)│              │ /ws/telemetry│       │
│        └──────────────┘              └──────┬───────┘       │
└─────────────────────────────────────────────┼───────────────┘
                                              │ Real-Time Stream
                                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 AERONEXGP FRONTEND (React 19)               │
│     Tactical HUD • Live Telemetry • Tracking • Analysis     │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Local Quick Start

### Prerequisites
* Python 3.10 or 3.11
* Node.js v18+ & npm
* Git

### Windows One-Click
Double-click `run_all.bat` to launch both servers simultaneously:
* **Frontend:** [http://localhost:5173](http://localhost:5173)
* **Backend API:** [http://localhost:8000](http://localhost:8000)
* **Interactive API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Manual Setup

#### 1. Backend
```bash
# Clone the repository
git clone https://github.com/sowdhanyarajkumar/AntiDrone_System.git
cd AntiDrone_System

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

#### 2. Frontend
```bash
# From repository root
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```

---

## 🧪 Automated Testing

Run the pytest suite to validate atmospheric math, database models, tracking solver, and REST endpoints:
```bash
pytest backend/tests -v
```

---

## ☁️ Deployment on Railway

The project includes pre-configured deployment files (`railway.json`, `Procfile`, `runtime.txt`, `requirements.txt`) that allow the entire application (React SPA + FastAPI + WebSocket) to run from a single container service.

1. Install Railway CLI: `npm install -g @railway/cli`
2. Link project: `railway link`
3. Deploy: `railway up`
4. Generate domain: `railway domain`

Live instance: **[https://aeronex-gp-production.up.railway.app](https://aeronex-gp-production.up.railway.app)**

---

## 📂 Project Directory Structure

```
Aeronex_GP/
├── backend/
│   ├── app/
│   │   ├── ai/            # YOLOv8 detector & model loaders
│   │   ├── api/           # REST endpoints (health, telemetry, tracking, etc.)
│   │   ├── core/          # Configuration & WebSocket manager
│   │   ├── database/      # SQLAlchemy models & SQLite setup
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Simulation orchestration & health engine
│   │   ├── simulation/    # Atmosphere, thermal, and disturbance physics
│   │   ├── tracking/      # Boresight tracking & pan/tilt solvers
│   │   ├── static/        # Pre-built production frontend assets
│   │   └── main.py        # FastAPI entrypoint & SPA static server
│   └── requirements.txt   # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── charts/        # Recharts live visualization components
│   │   ├── components/    # Navbar, Sidebar, SimulationControlPanel, MetricCard
│   │   ├── hooks/         # WebSocket stream hook with rolling buffer
│   │   ├── layouts/       # MainLayout with responsive mobile drawer
│   │   ├── pages/         # 10 HUD tactical views
│   │   └── services/      # REST API client
│   ├── package.json
│   └── vite.config.ts
├── docs/                  # Technical documentation & architecture guides
├── railway.json           # Railway cloud configuration
├── Procfile               # Production start command
└── README.md
```

---

## ⚖️ Safety & Scope Disclaimer

This software is an engineering research and simulation platform designed for environmental stress analysis, academic demonstration, and algorithmic verification. It contains no kinetic weapon integrations, RF jamming hardware drivers, or automated neutralization components.

