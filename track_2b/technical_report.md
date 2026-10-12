# Technical Report — ChronoMine AI (SwissTunnelCopilot)

- **Track:** Track 2B — Own Project
- **Event:** Hack Apertus Online (October 2026)
- **Author:** Romain Janz ([@winterstones](https://github.com/lightningstones) / GitLab: [@winterstones](https://gitlab.com/winterstones))
- **AI Co-Author & Assistant:** Antigravity (Google DeepMind)
- **GitHub Repository:** [lightningstones/apertus-chronomine](https://github.com/lightningstones/apertus-chronomine)
- **GitLab Mirror:** [winterstones/apertus-chronomine](https://gitlab.com/winterstones/apertus-chronomine)
- **Evaluation Dataset:** [winterstones/chronomine-subterranean-benchmark](https://huggingface.co/datasets/winterstones/chronomine-subterranean-benchmark)
- **Demo Video:** [2-minute prototype walkthrough](https://hackapertus.ch)

---

## 1. Summary

In major Swiss subterranean civil engineering projects (such as the second Gotthard road tube) and defense underground facilities (RUAG, armasuisse *Felskavernen*), site supervisors face two major bottlenecks: severe administrative overhead under Swiss standard contracts (**SIA 118**) across a heavily multilingual frontline workforce (where 40%–70% of miners speak Portuguese, Italian, or Spanish), and strict regulatory health and safety requirements (**SUVA / BauAV 2022**). Furthermore, because these underground works constitute critical national infrastructure or defense-sensitive assets, transmitting site logs, geotechnical data, and incident photos to foreign public cloud APIs (e.g., US-hosted models) is strictly prohibited. 

**ChronoMine AI** resolves this trilemma by coupling a lightweight, browser-native 3D subsurface situational awareness interface with the **Apertus v1.5** sovereign language and multimodal model. The platform ingests unstructured frontline observations in foreign languages, automatically synthesizes verified, legally grounded daily site journals (*Bautagebuch*) and unbudgeted force-account claims (*Regierapporte* under SIA 118 Art. 44) in official Swiss German and French, conducts multimodal visual audits against official SUVA life-saving rules, and operates in 100% air-gapped subterranean environments.

---

## 2. Architecture & Data Flow

### 2.1 Component Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHRONOMINE AI ARCHITECTURE                         │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 🌐 BROWSER / CLIENT LAYER            │ ⚙️ APPLICATION BACKEND (FastAPI)     │
│ • MapLibre GL JS + Three.js          │ • Pydantic Contract-First Validation │
│ • 3D Subsurface View (-Z altitude)   │ • Prompt Assembly & Grounding Engine │
│ • Interactive Cross-Section Canvas   │ • SUVA / BauAV Rule Engine           │
│ • Copilot Dialogue & Audit UI        │ • SIA 118 Bautagebuch Generator      │
└──────────────────────────────────────┴──────────────────────────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
       [Cloud Mode: Swiss AI]                       [Air-Gapped Mode: On-Site]
       CSCS Swiss Inference API                     Local GGUF / Ollama In-Tunnel
       api.inference.cscs.ch/v1                     Zero External Connection
       (Apertus v1.5-8B / 70B)                      (Apertus v1.5 Q4 Quantized)
```

### 2.2 Target Architecture (Mandatory Requirement)

ChronoMine AI fulfills the three mandatory deployment profiles:

1. **Air-Gapped (Primary Deployment Profile)**:
   - Deep Alpine tunnels (e.g., Sedrun shaft at 800m depth) and military bunkers operate without external internet.
   - ChronoMine AI bundles all assets locally: no external CDNs (`cdnjs`, `unpkg`, Google Fonts), local MapLibre/Three.js bundles, and on-premise local inference or bundled test fallback, guaranteeing 100% offline uptime.
2. **On-Premise**:
   - The entire system is containerized in Docker and deployable on the general contractor's local server or ruggedized on-site edge workstations with standard Make automation (`make run`).
3. **Sovereign Swiss Cloud**:
   - For connected sites, the backend connects natively to the sovereign Swiss AI inference endpoints: the **Swisscom AI Platform** (`api.swisscom.com`) hosting `swiss-ai/Apertus-v1.5-70B` and the Swiss National Supercomputing Centre (CSCS) in Lugano/Zurich, maintaining full compliance with Swiss Data Protection Law (nLPD) and Federal Public Procurement guidelines.

---

## 3. Use of Apertus

- **Model Selection:** `swiss-ai/Apertus-v1.5-70B` (primary high-capacity reasoning model deployed on Swisscom Sovereign Cloud) and `swiss-ai/Apertus-v1.5-8B` (for edge/on-premise deployment).
- **Modality & Capabilities Used:**
  1. *Multilingual Understanding*: Native coverage of vernacular Portuguese, Italian, Spanish, and regional terminology without external translation proxies.
  2. *Multimodal Vision*: Direct visual feature extraction from excavation photos (shotcrete integrity, rockbolt patterns, trench shoring, PPE compliance).
  3. *Long Context & Thinking Mode*: Ingesting comprehensive SUVA checklists and BauAV regulatory articles directly within the context window (up to 262k tokens) to produce referenced compliance rulings.
- **Deployment Location:** Live Swiss Sovereign Cloud inference via Swisscom AI Platform (`https://api.swisscom.com/products/swiss-ai-weeks/apertus-1.5-70b/v1`) and CSCS API with local quantized fallback for air-gapped subterranean validation.

---

## 4. Evaluation & Results

### 4.1 Evaluation Dataset (Track 2 Deliverable)
The project benchmarks Apertus v1.5 across a curated suite of 12 real-world subterranean construction scenarios deposited on Hugging Face:
- **Task A: Multilingual SIA 118 Structuring**: 6 test cases testing extraction fidelity, translation accuracy from PT/IT to Standard German/French, and formal compliance with SIA 118 Art. 44 claim requirements.
- **Task B: SUVA / BauAV Multimodal Safety Auditing**: 6 image-based inspection cases evaluating precision and recall on detecting critical safety non-compliances (excavation slopes, trench boxes, fall protection).

---

## 5. Limitations & Future Work

- Expanding the regulatory RAG corpus to cantonal environmental directives (e.g., tunnel wastewater pH neutralization under the *Gewässerschutzgesetz*).
- Direct bi-directional integration with Swiss construction ERP software (Sorba, smino).
