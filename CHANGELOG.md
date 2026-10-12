# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-12

### Added (Epic: SwissBau Copilot — Maîtrise d'Ouvrage & Conduite de Projet)
- **Strategic Pivot**: Transitioned from frontline site-log to an executive **Construction Project Developer & Owner (Bauherr) Copilot** powered by Swisscom Apertus v1.5-70B.
- **Infrastructure Decision Comparator (Pont vs Tunnel vs Tracé)**:
  - Multicriteria arbitration engine (`POST /api/project/infrastructure-arbitration`) balancing CapEx direct costs, litigation & neighbor opposition risk (LAT Art. 33 / OPB Art. 7 / Tribunal fédéral), environmental impact (ISOS / OFEV noise), and project duration.
  - Interactive weights sliders, key legal hurdles detection, and bilingual strategic executive summaries (FR/DE).
- **Tender Bid Comparison & Adjudication (SIA 118 / AIMP)**:
  - Public procurement analysis (`POST /api/project/tender-comparison`) detecting abnormally low bids (price dumping >15%), hidden geological risk exclusion clauses, and unbudgeted force-account claim risks (Art. 44).
- **Building Permit Opposition & Neighborhood Impact (LAT / OPB)**:
  - Neighbor grievance qualification engine (`POST /api/project/permit-opposition`) evaluating noise (OPB RS 814.41), building height & sunlight loss (Civil Code CC Art. 679/684), and construction traffic.
  - Generates formal rebuttal & conciliation response letters for municipal Building Commissions (*Baukommission*).
- **Official Swiss Open Data Pipeline (SBB CFF FFS & Fedlex)**:
  - Automated fetcher (`scripts/fetch_swiss_open_data.py`) synchronizing 289 Swiss railway tunnels (`swiss_railway_tunnels.geojson`), Gotthard Base Tunnel line 594 vectors (`gotthard_base_tunnel_sbb.geojson`), and 100 hectometre PK markers (`gotthard_km_points.geojson`).
  - Ingested full Fedlex BauAV 2022 (RS 832.311.141, 101 articles), SUVA 84043 vital rules, and SIA 118 core articles.
- **Executive Decision Report PDF Exporter**:
  - Vector ReportLab engine (`POST /api/project/export-decision-pdf`) generating official A4 Swiss Infrastructure Strategic Decision Reports with comparison matrix, legal obstacles, and owner signature blocks.
- **Comprehensive Test Suite**:
  - 18/18 pytest tests green (100% pass rate) with live Apertus-70B inference verification.

## [1.0.0] - 2026-10-12

### Added
- **Hack Apertus 2026 Submission**: Track 2B (Own Project) subterranean sovereign compliance copilot for Swiss tunnel and defense civil engineering.
- **3D Tactical Subsurface Engine**: WebGL-accelerated negative altitude ($-Z$) browser map with translucent alpine terrain, milestone markers (PK), and real-time miner beacon positions using MapLibre GL JS & Three.js.
- **Multilingual SIA 118 Bautagebuch & Regierapport Generator**: Ingests raw voice and text field logs in Portuguese, Italian, Spanish, or French and synthesizes official German or French daily journals (*Bautagebuch*) with force-account claims (*Regierapporte*) under SIA 118 Art. 44.
- **SUVA & BauAV 2022 Safety Violation Auditor**: Audits underground trench and tunnel conditions against Swiss safety ordinances (BauAV Art. 15, 51, 54, 80) with automatic Stop-Work Order issuance.
- **Sovereign Swiss Cloud Integration**: Native connection to the **Swisscom Sovereign AI Platform** hosting `swiss-ai/Apertus-v1.5-70B` under Swiss data residency.
- **Deterministic Air-Gapped Engine**: Offline regulatory fallback for isolated subterranean shafts and military defense bunkers.
- **Evaluation Benchmark Dataset**: 6 test cases deposited on Hugging Face (`winterstones/chronomine-subterranean-benchmark`) evaluating Apertus 1.5-70B with 100% accuracy.
- **Official Technical Report**: Pre-compiled 2-page PDF report (`track_2b/ChronoMine_Report.pdf`) strictly adhering to the 6-page maximum hackathon limit.
- **Docker Containerization**: Self-contained multi-stage build runnable with root `make run` for judges evaluation.
- **Official SIA 118 PDF Export**: Vector ReportLab engine generating formal A4 Swiss Bautagebuch & Regierapport PDF documents with cost breakdowns, downtime tracking, and signature blocks.
- **SUVA Multimodal Visual Inspection**: Pre-built tactical inspection graphics and scenario switcher covering BauAV Art. 54 (trenches), BauAV Art. 15 (scaffolding), and SIA 198 (subterranean rockface crown stability).
- **Live Sovereignty & Data Residency Badge**: Dynamic UI indicator reflecting active Swisscom Cloud (`swiss-ai/Apertus-v1.5-70B`) or local air-gapped subterranean node under Swiss nLPD law.
- **Official SBB CFF FFS Open Government Data Pipeline**: Automated downloader (`fetch_swiss_open_data.py`) querying `data.sbb.ch` for all 289 Swiss railway tunnels, Linie 594 (Gotthard-Basistunnel 57.1 km) track vectors, and official hectometre PK markers.
- **Gotthard Base Tunnel Digital Twin (-800m)**: Authentic subterranean modeling replacing synthetic mocks with the real Gotthard Base Tunnel Sedrun Multifunktionsstelle (SMF Sedrun), parallel single-track tubes (40m spacing), and cross-passages QS-40 to QS-45.
- **Fedlex & SUVA Swiss Knowledge Base**: Ingested SR 832.311.141 (Bauarbeitenverordnung 2022), SUVA 84043 (10 règles vitales pour les travaux souterrains), and SIA 118 (Art. 44–46) regulatory corpora.


