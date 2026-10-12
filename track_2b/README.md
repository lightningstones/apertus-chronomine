# ChronoMine AI — SwissTunnelCopilot 🚇🇨🇭

> **Sovereign Air-Gapped Subterranean Situation Awareness & Compliance Copilot**  
> Powered by **Apertus v1.5** (Swiss AI Initiative)  
> **Hack Apertus — Track 2B: Own Project**

---

## 📌 Overview

In Switzerland, deep Alpine tunnel projects (Gotthard Base Tunnel, 2nd Gotthard Road Tube) and defense underground facilities (RUAG, armasuisse *Felskavernen*) operate under two critical constraints:
1. **Zero Foreign Cloud Access (Air-Gap & Sovereignty)**: Critical infrastructure data and defense plans are legally prohibited from leaving Swiss jurisdiction or being routed through US cloud APIs. Deep tunnels frequently operate with zero internet connection.
2. **The Multilingual Field Communication Gap**: 40% to 70% of frontline miners speak Portuguese, Italian, Spanish, or Albanian, while Swiss engineering norms (**SIA 118**, **SIA 198**) and safety standards (**SUVA / BauAV 2022**) mandate rigorous reporting in Standard German (*Schriftdeutsch*) or French.

**ChronoMine AI** combines an interactive 3D subsurface tactical situation awareness engine (MapLibre GL JS + Three.js) with **Apertus v1.5** to deliver:
- 🗺️ **3D Subsurface Situational Awareness**: Real-time negative altitude ($-Z$) tactical tunnel mapping with translucent ground and localized milestone (PK) markers.
- 📝 **Multilingual Bautagebuch & Regierapport (SIA 118)**: Frontline workers input field voice/notes in Portuguese or Italian; Apertus translates and structures official German/French daily site logs (*Bautagebuch*) and unbudgeted force-account claims (*Regierapporte* under SIA 118 Art. 44).
- 📸 **Multimodal SUVA & BauAV Safety Audit**: Upload tunnel face or excavation photos; Apertus analyzes support conditions, identifies safety hazards, and cites exact BauAV articles and SUVA life-saving rules.
- 🔒 **100% Air-Gapped Sovereign Deployment**: Runs entirely locally or on the Swiss National Supercomputing Centre (CSCS) infrastructure.

---

## 🏗️ Target Architecture (Mandatory Compliance)

ChronoMine AI natively supports all 3 hackathon deployment models:
- **a) On-Premise**: Runs locally inside the contractor's or facility's local server network.
- **b) Air-Gapped**: 100% operational underground inside the tunnel with zero internet connectivity and zero external CDN dependencies.
- **c) Sovereign Swiss Cloud**: Directly interfaces with the official Swiss CSCS Apertus inference endpoints under Swiss data residency.

---

## 🚀 Quick Start

### 1. Run with Docker (Hackathon Official Run)
From the project root or inside `track_2b/`:
```bash
make run
```
Then open your browser at **`http://localhost:8000`**.

### 2. Local Development (Without Docker)
```bash
cd track_2b
pip install -r requirements.txt
cp .env.example .env
make dev
```

---

## 📂 Repository Structure

```
track_2b/
├── Makefile              # `make run` spins up the container
├── Dockerfile            # Container definition for complete offline run
├── docker-compose.yml    # Service orchestration
├── requirements.txt      # Python dependencies (FastAPI, Pydantic, etc.)
├── .env.example          # Environment variables (CSCS API / Offline mode)
├── technical_report.md   # Official 6-page Hackathon Technical Report
├── src/
│   ├── backend/          # FastAPI backend & Apertus provider engine
│   │   ├── main.py       # API routes
│   │   ├── provider.py   # Apertus API / Offline mock adapter
│   │   └── models.py     # Pydantic schemas (Contract-First)
│   └── frontend/         # 3D Tactical Map (MapLibre + Three.js) & Copilot UI
├── data/
│   ├── knowledge/        # SUVA rules & SIA 118 schema
│   ├── demo/             # Multilingual test notes & inspection photos
│   ├── geo/              # GeoJSON tunnel geometry & miner coordinates
│   └── huggingface/      # Evaluation benchmark dataset (Track 2)
└── docs/                 # Architecture diagrams & ADRs
```
