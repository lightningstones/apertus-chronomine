# EPIC v2.0.0 — SwissBau Copilot (Maîtrise d'Ouvrage & Conduite de Projet) 🇨🇭🏗️

> **Statut :** Terminé & Validé (18/18 Tests Pytest Verts)  
> **Modèle IA :** Swisscom Apertus v1.5-70B (Souveraineté CSCS / NLPD)  
> **Auteurs :** Romain Janz & Antigravity (Google DeepMind)  
> **Date de bascule :** 12 Octobre 2026  

---

## 🎯 1. Contexte & Justification du Pivot Stratégique (Le Changement de Direction)

### Le Problème Initial (v1.0.0) :
La version 1.0.0 ciblait le chef de chantier de premier niveau en souterrain (journal de chantier multilingue et photos de chantier).  
Cependant :
1. **Apertus v1.5-70B est un grand modèle de langage textuel et juridique**, et **non un modèle de vision par ordinateur**. Prétendre analyser des photos d'échafaudages ou de parois rocheuses avec un LLM textuel était sous-optimal.
2. La véritable valeur d'Apertus réside dans son **intelligence textuelle, juridique et multilingue suisse** (droit fédéral, normes SIA, jurisprudence du Tribunal fédéral, conciliation cantonale).
3. Le plus fort impact économique et décisionnel dans la construction suisse se situe au niveau du **Maître d'Ouvrage (Bauherr)**, du **Chargé de projet** et des **Directeurs de travaux**.

### La Vision v2.0.0 :
Faire pivoter la solution vers un **Copilote Stratégique d'Aide à la Décision pour Maître d'Ouvrage & Développeur d'Infrastructures**.

```
                           ┌──────────────────────────────────────────────┐
                           │            SWISSBAU COPILOT v2.0.0           │
                           │   Copilote Décisionnel Maître d'Ouvrage      │
                           └──────────────────────┬───────────────────────┘
                                                  │
            ┌─────────────────────────────────────┼─────────────────────────────────────┐
            ▼                                     ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────┐             ┌───────────────────────┐
│  Arbitrage Stratégique│             │ Comparaison d'Offres  │             │   Gestion Oppositions │
│    PONT vs TUNNEL     │             │    SIA 118 / AIMP     │             │     LAT / OPB / CC    │
├───────────────────────┤             ├───────────────────────┤             ├───────────────────────┤
│ • CapEx vs 50y OpEx   │             │ • Détection dumping   │             │ • Qualification griefs│
│ • Risque recours LAT  │             │ • Risques régie Art 44│             │ • Étude bruit OPB     │
│ • Protection ISOS/LPE │             │ • Clauses pièges sol  │             │ • Lettre de levée     │
│ • Matrice décision    │             │ • Adjudication légale │             │ • Conciliation        │
└───────────────────────┘             └───────────────────────┘             └───────────────────────┘
```

---

## 🏛️ 2. Piliers Fonctionnels de l'Epic v2.0.0

### Pilier 1 : Arbitrage Multicritères Pont vs Tunnel (Infrastructure Decision Matrix)
* **Demande utilisateur verbatim :**  
  > *"une maniere de proposer des comparatife pour la decision de la construction d'un pont ou d'un tunnel le meilleurs emplacement qui allie oposition et recoure, prix , delaie et impact"*
* **Évaluation pondérée :**
  - **Risque d'Opposition & Recours Juridiques (35%)** : Analyse des chances de recours des riverains et associations (LAT Art. 33, recours au Tribunal fédéral).
  - **Coût d'Investissement Direct (CapEx) (25%)** : Normalisation des coûts financiers.
  - **Impact Environnemental & Paysager (25%)** : Respect de l'OPB (Ordonnance sur le bruit, RS 814.41) et de l'inventaire ISOS (protection des sites bâtis).
  - **Délais de Réalisation (15%)** : Durée de chantier + délais de procédure contentieuse.
* **Livrables :**
  - Endpoint `POST /api/project/infrastructure-arbitration`
  - Recommandation exécutive bilingue (FR / DE)
  - Visualisation des portails et tracés sur la carte interactive SBB CFF FFS.

### Pilier 2 : Comparateur d'Offres & Adjudication (SIA 118 / AIMP)
* **Normes suisses :** SIA 118 (Art. 4, Art. 24, Art. 38, Art. 44 régies, Art. 58 responsabilité du sol) et AIMP (Accord intercantonal sur les marchés publics).
* **Détections IA :**
  - Détection des offres anormalement basses (>15% à 18% sous le devis estimatif) génératrices de litiges et de surcoûts en régie.
  - Détection des clauses d'exclusion illicites (ex: clause écartant la responsabilité des aléas géologiques).
* **Livrable :** Endpoint `POST /api/project/tender-comparison`.

### Pilier 3 : Qualification d'Oppositions de Permis de Construire (LAT / OPB)
* **Bases juridiques :**
  - LAT (Loi fédérale sur l'aménagement du territoire, RS 700)
  - OPB (Ordonnance sur la protection contre le bruit, RS 814.41)
  - CC (Code civil suisse, RS 210, Art. 679 et 684 sur les immissions et perte d'ensoleillement)
  - LPE (Loi sur la protection de l'environnement, RS 814.01)
* **Livrables :**
  - Qualification juridique des griefs (Bruit, Gabarit/Hauteur, Trafic poids lourds, Paysage).
  - Lettre formelle de réfutation et conciliation pour la Commission des constructions (*Baukommission*).
  - Endpoint `POST /api/project/permit-opposition`.

### Pilier 4 : Rapport Décisionnel A4 Officiel (PDF Exporter)
* Génération ReportLab d'un document contractuel complet : cartouche, synthèse exécutive, tableau comparatif des variantes, bases juridiques suisses et signatures du Maître d'Ouvrage (*Bauherr*).
* Endpoint `POST /api/project/export-decision-pdf`.

---

## 📊 3. Données Réelles Suisses Intégrées (Open Government Data)

| Source | Fichier | Contenu Réel |
|---|---|---|
| **CFF Open Data (data.sbb.ch)** | `data/geo/swiss_railway_tunnels.geojson` | 289 tunnels ferroviaires officiels suisses avec longueurs et coordonnées |
| **CFF Trajectoire Gotthard** | `data/geo/gotthard_base_tunnel_sbb.geojson` | 5 vecteurs géométriques réels de la ligne 594 (Sedrun, Bodio, Erstfeld) |
| **CFF Hectomètres PK** | `data/geo/gotthard_km_points.geojson` | 100 bornes hectométriques officielles |
| **Fedlex (fedlex.admin.ch)** | `data/knowledge/fedlex_bauav_2022.json` | Ordonnance sur les travaux de construction (RS 832.311.141), 101 articles |
| **SUVA (suva.ch)** | `data/knowledge/suva_vital_rules_underground.json` | 10 règles vitales SUVA travaux souterrains (SUVA 84043) |
| **SIA Normes** | `data/knowledge/sia_118_articles.json` | SIA 118 (Conditions générales pour l'exécution des travaux de construction) |

---

## 🧪 4. Matrice de Validation des Tests (18/18 Pytest Verts)

```
track_2b/tests/test_api.py::test_health_check PASSED                     [ 5%]
track_2b/tests/test_api.py::test_get_tunnels_geojson PASSED              [11%]
track_2b/tests/test_api.py::test_get_miners_geojson PASSED               [16%]
track_2b/tests/test_api.py::test_bautagebuch_multilingual_portuguese PASSED [22%]
track_2b/tests/test_api.py::test_suva_safety_audit_trench_hazard PASSED  [27%]
track_2b/tests/test_api.py::test_frontend_index_html PASSED              [33%]
track_2b/tests/test_api.py::test_get_demo_field_notes PASSED             [38%]
track_2b/tests/test_api.py::test_get_demo_suva_rules PASSED              [44%]
track_2b/tests/test_api.py::test_system_status PASSED                    [50%]
track_2b/tests/test_api.py::test_bautagebuch_pdf_export PASSED           [55%]
track_2b/tests/test_api.py::test_demo_images_static PASSED               [61%]
track_2b/tests/test_api.py::test_swiss_railway_tunnels_ogd PASSED        [66%]
track_2b/tests/test_api.py::test_gotthard_base_tunnel_geometry PASSED    [72%]
track_2b/tests/test_api.py::test_fedlex_and_suva_knowledge PASSED        [77%]
track_2b/tests/test_api.py::test_infrastructure_arbitration_bridge_vs_tunnel PASSED [83%]
track_2b/tests/test_api.py::test_tender_comparison_sia_118 PASSED        [88%]
track_2b/tests/test_api.py::test_permit_opposition_evaluation PASSED     [94%]
track_2b/tests/test_api.py::test_export_decision_pdf PASSED              [100%]
============================= 18 passed in 45.86s =============================
```
