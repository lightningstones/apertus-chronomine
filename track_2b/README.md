# SwissBau Copilot — Apertus AI (ChronoMine) 🏗️🇨🇭

> **Version 2.0.0 (Epic: Maîtrise d'Ouvrage & Conduite de Projet)**  
> **Sovereign Construction Project Developer & Owner (Bauherr) Copilot**  
> Powered by **Apertus v1.5-70B** (Swiss AI Initiative / Swisscom Cloud / CSCS)  
> **Hack Apertus — Track 2B: Own Project**  
> 📖 *Documentation détaillée de l'Epic :* [`docs/EPIC_V2_SWISSBAU_COPILOT.md`](docs/EPIC_V2_SWISSBAU_COPILOT.md) · [`CHANGELOG.md`](../CHANGELOG.md)

---

## 📌 Overview & Strategic Direction (v2.0.0)

In Switzerland, large infrastructure projects (Gotthard crossings, alpine tunnels, viaducts, urban developments) operate under extreme legal, environmental, and financial constraints:
1. **High Legal & Opposition Exposure**: Neighbor complaints under the **Noise Abatement Ordinance (OPB RS 814.41)**, appeals to the **Federal Supreme Court (Tribunal fédéral)** under the **Spatial Planning Act (LAT RS 700 Art. 33)**, and heritage protection under **ISOS** routinely paralyze projects for 2 to 5 years.
2. **Public Procurement Risks (SIA 118 / AIMP)**: Abnormally low tender bids (price dumping) frequently hide exclusions of geotechnical risks that erupt as costly unbudgeted force-account claims (*Regierapporte* under SIA 118 Art. 44).
3. **Data Residency & Sovereignty**: Infrastructure plans, sensitive cost models, and legal strategies cannot leave Swiss borders under the revised **Federal Act on Data Protection (nLPD)**.

**SwissBau Copilot v2.0.0** harnesses **Swisscom Apertus v1.5-70B** as an executive assistant for **Project Owners (Maîtres d'Ouvrage / Bauherren)** and **Project Managers**:
- 🌉 **Pont vs Tunnel Strategic Decision Comparator**: Multicriteria arbitration weighing legal opposition risk (35%), direct CapEx (25%), environmental/noise impact (25%), and schedule delays (15%).
- 📑 **Tender Bid Comparison & Adjudication (SIA 118 / AIMP)**: Detects price dumping (>15%), flags hidden contractual clauses, and drafts legal award rationales.
- ⚖️ **Building Permit Opposition & Rebuttal (LAT / OPB)**: Categorizes neighbor grievances, calculates estimated procedural delays, and writes official rebuttal letters for municipal Building Commissions (*Baukommissionen*).
- 📄 **Executive PDF Exporter**: Instant vector ReportLab generation of official A4 Decision Reports with cartouche and signature blocks.
- 🗺️ **SBB CFF FFS Vector Digital Twin**: Live Open Data integration with 289 Swiss railway tunnels and the Gotthard Base Tunnel (-800m).
- 📝 **Frontline Bautagebuch & SUVA Audit**: Preserved frontline multilingual daily logs and BauAV 2022 safety checks.

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
└── docs/                 # Architecture diagrams, ADRs & demo video script
```

---

## 🔗 Project Links

- **GitHub Repository**: [https://github.com/lightningstones/apertus-chronomine](https://github.com/lightningstones/apertus-chronomine)
- **GitLab Mirror**: [https://gitlab.com/winterstones/apertus-chronomine](https://gitlab.com/winterstones/apertus-chronomine)
- **Hugging Face Benchmark Dataset**: [https://huggingface.co/datasets/winterstones/chronomine-subterranean-benchmark](https://huggingface.co/datasets/winterstones/chronomine-subterranean-benchmark)
- **Epic v2.0.0 Roadmap & Specifications**: [`track_2b/docs/EPIC_V2_SWISSBAU_COPILOT.md`](docs/EPIC_V2_SWISSBAU_COPILOT.md)
- **Technical Report**: [`track_2b/technical_report.md`](technical_report.md) & [`track_2b/ChronoMine_Report.pdf`](ChronoMine_Report.pdf)

---

## 👥 Authors & AI Attribution

- **Lead Author & Engineering**: Romain Janz ([@winterstones](https://gitlab.com/winterstones) / [@lightningstones](https://github.com/lightningstones))
- **AI Co-Author & Pair Programmer**: Antigravity (Google DeepMind)
- **License**: [Apache-2.0](../LICENSE) (Permissive Open Source)
