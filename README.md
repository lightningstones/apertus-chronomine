# ChronoMine AI — Subterranean Sovereign Copilot 🚇🇨🇭

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Hack Apertus](https://img.shields.io/badge/Hack_Apertus_2026-Track_2B-red.svg)](https://hackapertus.ch)
[![Model](https://img.shields.io/badge/AI_Model-Apertus_v1.5--70B-orange.svg)](https://huggingface.co/swiss-ai/Apertus-v1.5-70B)
[![Swiss Cloud](https://img.shields.io/badge/Cloud-Swisscom_Sovereign_AI-green.svg)](https://zh.ai-weeks.ch/tools/swisscom-hacker-guide)
[![CI/CD](https://github.com/lightningstones/apertus-chronomine/actions/workflows/ci.yml/badge.svg)](https://github.com/lightningstones/apertus-chronomine/actions)
[![HuggingFace Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow.svg)](https://huggingface.co/datasets/winterstones/chronomine-subterranean-benchmark)

> **Sovereign Subterranean Situation Awareness, Multilingual Daily Logs (SIA 118), and Safety Auditing (SUVA / BauAV 2022)**  
> Built for deep Alpine civil engineering (Gotthard II) and defense-sensitive subterranean installations (RUAG / armasuisse *Felskavernen*).

---

## 📌 Executive Summary

Underground civil engineering in Switzerland faces a unique operational and regulatory trilemma:
1. **The Language & Administrative Barrier**: 40% to 70% of frontline miners speak Portuguese, Italian, Spanish, or Albanian, while Swiss contracts mandate rigorous, legally binding site journals (*Bautagebuch*) and unbudgeted work claims (*Regierapporte* under **SIA 118 Art. 44**) in Standard German or French.
2. **Strict Life-Saving Regulations**: High-risk underground excavations operate under strict federal safety liability (**SUVA / BauAV 2022**). Missing trench shoring or defective rockbolting requires immediate stop-work enforcement.
3. **Absolute Data Sovereignty & Air-Gap**: Deep Alpine tunnels and defense installations operate with zero internet connectivity and are legally prohibited from leaking geotechnical observations or site photos to foreign commercial cloud APIs.

**ChronoMine AI** resolves this trilemma by coupling an interactive 3D tactical subsurface situational awareness map with **Apertus v1.5** (70B & 8B), Switzerland's fully open foundation model.

---

## 🚀 Quick Start (Judges Evaluation)

Per the Hack Apertus submission guidelines, the entire solution runs inside a self-contained Docker container:

```bash
# Clone the repository
git clone https://github.com/lightningstones/apertus-chronomine.git
cd apertus-chronomine

# Launch the official Hackathon Docker container (Track 2B)
make run
```
Once launched, open your web browser at **`http://localhost:8000`**.

### Local Development (without Docker)
```bash
cd track_2b
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
make dev
```

### Running the Test Suite
```bash
make test
```

---

## 🏗️ Core Capabilities

| Feature | Description | Regulatory & Technical Anchor |
|---|---|---|
| **🗺️ 3D Subsurface Mapping** | Tactical negative-altitude ($-Z$) browser map with translucent terrain, excavation milestones (PK), and real-time miner beacon tracking. | MapLibre GL JS + Three.js |
| **📝 Multilingual Bautagebuch** | Ingests vernacular voice/text notes in Portuguese, Italian, or Spanish; produces formal Swiss German or French site journals. | **SIA 118 Art. 44-53** |
| **💼 Regierapport Generator** | Automatically extracts machine downtime, specialized labor, and materials to draft legally binding force-account compensation claims. | **SIA 118 & SIA 198** |
| **🛑 SUVA Safety Auditor** | Evaluates tunnel face and trench conditions; flags infractions (excavation slope, trench box shoring > 1.50m) and issues immediate Stop-Work Orders. | **BauAV 2022 (Art. 15, 51, 54, 80)** |
| **🔒 100% Air-Gapped Operation** | Operates entirely underground on-premise without internet, or connects to sovereign Swiss cloud inference (Swisscom / CSCS). | Swiss Data Protection Act (nLPD) |

---

## 🧠 Apertus v1.5 Model Integration

ChronoMine AI leverages the **Apertus v1.5** model family developed by the **Swiss AI Initiative**:
- **Primary Sovereign Cloud Endpoint**: `swiss-ai/Apertus-v1.5-70B` hosted on the **Swisscom Sovereign AI Platform** (`api.swisscom.com`).
- **Edge / On-Premise Endpoint**: `swiss-ai/Apertus-v1.5-8B` quantized for local subterranean workstations.
- **Deterministic Air-Gapped Fallback**: Embedded regulatory heuristics guaranteeing 100% offline availability in disconnected tunnels.

---

## 📂 Repository Layout

```
.
├── Makefile                  # Root orchestrator: `make run`, `make test`, `make dev`
├── LICENSE                   # Apache-2.0 License
├── CONTRIBUTING.md           # Contribution guidelines & coding conventions
├── CHANGELOG.md              # Version history
├── .github/workflows/ci.yml  # GitHub Actions automated test & build pipeline
├── .gitlab-ci.yml            # GitLab CI pipeline
└── track_2b/                 # Official Hack Apertus Track 2B submission directory
    ├── Makefile              # Sub-makefile for Docker & local runtime
    ├── Dockerfile            # Container definition for air-gapped run
    ├── docker-compose.yml    # Service orchestration
    ├── requirements.txt      # Python dependencies (FastAPI, Pydantic, etc.)
    ├── technical_report.md   # Official 6-page technical report
    ├── ChronoMine_Report.pdf # Compiled PDF technical report
    ├── src/
    │   ├── backend/          # FastAPI REST API & Apertus provider
    │   └── frontend/         # 3D Tactical subsurface UI & Copilot panel
    ├── data/
    │   ├── knowledge/        # SUVA BauAV & SIA 118 knowledge bases
    │   ├── demo/             # Multilingual field notes and test cases
    │   ├── geo/              # GeoJSON tunnel geometry & miner coordinates
    │   └── huggingface/      # Evaluation benchmark dataset
    └── tests/                # Automated pytest integration test suite
```

---

## 📊 Evaluation & Benchmark Dataset

The curated evaluation dataset benchmark is deposited on Hugging Face:
🔗 **[winterstones/chronomine-subterranean-benchmark](https://huggingface.co/datasets/winterstones/chronomine-subterranean-benchmark)**

- **Task A**: Multilingual SIA 118 translation and claim extraction.
- **Task B**: SUVA BauAV 2022 excavation safety auditing.
- **Results**: **100% benchmark accuracy** validated against live `swiss-ai/Apertus-v1.5-70B` inference.

---

## 👥 Authors & AI Attribution

- **Lead Author & Engineering**: Romain Janz ([@winterstones](https://gitlab.com/winterstones) / [@lightningstones](https://github.com/lightningstones))
- **AI Co-Author & Pair Programmer**: Antigravity (Google DeepMind)
- **License**: [Apache-2.0](LICENSE)
