/**
 * ChronoMine AI — app.js
 * Subterranean Situation Awareness & SIA 118 / SUVA Copilot (Apertus v1.5)
 */

'use strict';

const CONFIG = {
  CENTER: [8.7690, 46.6660],
  ZOOM_DEFAULT: 16,
  ZOOM_MIN: 14,
  ZOOM_MAX: 20,
  TILE_URL: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  TILE_ATTRIBUTION: '© OpenStreetMap contributors | ChronoMine AI (Apertus)',
  TUNNELS_URL: '/api/geo/tunnels',
  MINERS_URL: '/api/geo/miners',
  DEMO_NOTES_URL: '/api/demo/notes'
};

class ChronoMineApp {
  constructor() {
    this.map = null;
    this.tunnelsData = null;
    this.minersData = null;
    this.demoNotes = [];
    this.incidentMarker = null;
    this.arbitrageMarkers = [];
    this.is3D = false;
    this.lastBautagebuchResponse = null;
    this.lastArbitrageResponse = null;
  }

  async init() {
    this.setupClock();
    this.setupTabs();
    this.setupCopilotEvents();
    this.setupStrategicEvents();
    await this.loadSystemStatus();
    await this.initMap();
    await this.loadData();
    this.setupMapControls();
  }

  async loadSystemStatus() {
    try {
      const res = await fetch('/api/system/status');
      if (!res.ok) return;
      const data = await res.json();
      const pillMode = document.getElementById('pill-mode');
      const badgePill = document.getElementById('badge-sovereign-status');
      if (pillMode) {
        if (data.provider === 'swisscom' || data.provider === 'cscs') {
          const modelName = (data.model || 'Apertus-70B').replace('swiss-ai/', '');
          pillMode.textContent = `SWISSCOM CLOUD (${modelName})`;
          if (badgePill) badgePill.title = `Souverain Suisse · Swisscom Cloud / CSCS Lugano · nLPD Conforme`;
        } else {
          pillMode.textContent = 'AIR-GAP LOCAL NODE';
          if (badgePill) badgePill.title = `Mode Hors-Ligne Souverain · Aucun appel cloud sortant`;
        }
      }
    } catch (e) {
      console.warn("Could not fetch system status:", e);
    }
  }

  setupClock() {
    const el = document.getElementById('clock');
    const update = () => {
      const now = new Date();
      el.textContent = now.toTimeString().split(' ')[0];
    };
    setInterval(update, 1000);
    update();
  }

  setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab');
        const target = document.getElementById(targetId);
        if (target) target.classList.add('active');
      });
    });
  }

  async initMap() {
    this.map = new maplibregl.Map({
      container: 'map',
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: [CONFIG.TILE_URL],
            tileSize: 256,
            attribution: CONFIG.TILE_ATTRIBUTION,
            maxzoom: 19
          }
        },
        layers: [{
          id: 'osm-tiles',
          type: 'raster',
          source: 'osm',
          paint: {
            'raster-brightness-min': 0,
            'raster-brightness-max': 0.25,
            'raster-saturation': -0.6,
            'raster-contrast': 0.1
          }
        }]
      },
      center: CONFIG.CENTER,
      zoom: CONFIG.ZOOM_DEFAULT,
      minZoom: CONFIG.ZOOM_MIN,
      maxZoom: CONFIG.ZOOM_MAX,
      maxPitch: 85,
      pitchWithRotate: true
    });

    this.map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');
    this.map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');

    return new Promise(resolve => this.map.on('load', resolve));
  }

  async loadData() {
    try {
      const [tunnelsRes, minersRes, notesRes] = await Promise.all([
        fetch(CONFIG.TUNNELS_URL),
        fetch(CONFIG.MINERS_URL),
        fetch(CONFIG.DEMO_NOTES_URL)
      ]);

      this.tunnelsData = await tunnelsRes.json();
      this.minersData = await minersRes.json();
      this.demoNotes = await notesRes.json();

      this.renderTunnels(this.tunnelsData);
      this.renderMiners(this.minersData);
      this.renderMinersSidebar(this.minersData);
    } catch (e) {
      console.warn("Could not load backend datasets, using inline fallback:", e);
    }
  }

  renderTunnels(geojson) {
    if (!geojson) return;
    this.map.addSource('tunnels-source', { type: 'geojson', data: geojson });

    // Tunnel lines
    this.map.addLayer({
      id: 'tunnels-line',
      type: 'line',
      source: 'tunnels-source',
      filter: ['==', '$type', 'LineString'],
      paint: {
        'line-color': [
          'match', ['get', 'type'],
          'main_gallery', '#1e88e5',
          'cross_gallery', '#00acc1',
          'access_tunnel', '#43a047',
          'evacuation_tunnel', '#fdd835',
          '#c62828'
        ],
        'line-width': 5,
        'line-opacity': 0.85
      }
    });

    // Chambers / rooms
    this.map.addLayer({
      id: 'rooms-fill',
      type: 'fill',
      source: 'tunnels-source',
      filter: ['==', '$type', 'Polygon'],
      paint: {
        'fill-color': 'rgba(33, 150, 243, 0.35)',
        'fill-outline-color': '#00bcd4'
      }
    });
  }

  renderMiners(geojson) {
    if (!geojson) return;
    this.map.addSource('miners-source', { type: 'geojson', data: geojson });

    this.map.addLayer({
      id: 'miners-points',
      type: 'circle',
      source: 'miners-source',
      paint: {
        'circle-radius': 7,
        'circle-color': [
          'match', ['get', 'status'],
          'active', '#00e676',
          'alert', '#ff9100',
          '#546e7a'
        ],
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff'
      }
    });
  }

  renderMinersSidebar(geojson) {
    const list = document.getElementById('miners-list');
    if (!list || !geojson || !geojson.features) return;
    list.innerHTML = '';

    geojson.features.forEach(f => {
      const p = f.properties;
      const item = document.createElement('div');
      item.style.cssText = 'padding:8px; border-bottom:1px solid var(--border); font-family:var(--font-mono); font-size:11px; display:flex; justify-content:space-between; align-items:center; cursor:pointer;';
      item.innerHTML = `
        <div>
          <span style="color:var(--text-accent); font-weight:bold;">${p.badge}</span> ${p.name}
          <div style="font-size:9px; color:var(--text-muted);">${p.sector || 'Tunnel'} (${p.depth_m}m)</div>
        </div>
        <div style="font-size:10px; color:${p.status === 'alert' ? '#ff9100' : '#00e676'};">${p.status.toUpperCase()}</div>
      `;
      item.addEventListener('click', () => {
        this.map.flyTo({ center: f.geometry.coordinates, zoom: 18, pitch: 45 });
      });
      list.appendChild(item);
    });
  }

  setupMapControls() {
    document.getElementById('btn-center')?.addEventListener('click', () => {
      this.map.flyTo({ center: CONFIG.CENTER, zoom: CONFIG.ZOOM_DEFAULT, pitch: 0, bearing: 0 });
    });

    document.getElementById('btn-3d-view')?.addEventListener('click', (e) => {
      this.is3D = !this.is3D;
      e.currentTarget.classList.toggle('active', this.is3D);
      const pitch = this.is3D ? 65 : 0;
      const bearing = this.is3D ? -25 : 0;
      this.map.easeTo({ pitch, bearing, duration: 1000 });
      document.getElementById('subsurface-3d-controls')?.classList.toggle('hidden', !this.is3D);
    });

    document.getElementById('btn-depth-view')?.addEventListener('click', (e) => {
      const panel = document.getElementById('depth-panel');
      panel?.classList.toggle('hidden');
      e.currentTarget.classList.toggle('active');
    });

    document.getElementById('btn-close-depth')?.addEventListener('click', () => {
      document.getElementById('depth-panel')?.classList.add('hidden');
      document.getElementById('btn-depth-view')?.classList.remove('active');
    });
  }

  setupCopilotEvents() {
    // Select sample note
    const selNote = document.getElementById('sel-sample-note');
    selNote?.addEventListener('change', (e) => {
      const selectedId = e.target.value;
      const note = this.demoNotes.find(n => n.id === selectedId);
      if (note) {
        document.getElementById('txt-note-content').value = note.raw_text;
        document.getElementById('txt-author-name').value = note.author_name;
      }
    });

    // Generate Bautagebuch button
    const btnSia = document.getElementById('btn-generate-sia');
    btnSia?.addEventListener('click', async () => {
      btnSia.textContent = "⏳ Analyse Apertus v1.5...";
      btnSia.disabled = true;

      const rawText = document.getElementById('txt-note-content').value;
      const author = document.getElementById('txt-author-name').value;
      const lang = document.getElementById('sel-target-lang').value;

      try {
        const res = await fetch('/api/copilot/bautagebuch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            raw_text: rawText,
            author_name: author,
            target_language: lang,
            location_pk: 'PK 3.200 (Galerie Nord)'
          })
        });
        const data = await res.json();
        this.lastBautagebuchResponse = data;

        // Render card
        const card = document.getElementById('card-sia-result');
        const pre = document.getElementById('pre-sia-output');
        const badge = document.getElementById('badge-sia-regie');

        card.classList.remove('hidden');
        badge.textContent = `Regierapport SIA 118 Art. 44 : ${data.regierapport.is_required ? 'OUI' : 'NON'}`;
        pre.textContent = data.official_log_entry;

        // Update alert count in header
        if (data.safety_hazard_detected) {
          const alertPill = document.getElementById('alert-count');
          if (alertPill) alertPill.textContent = '1 ALERTE SUVA';
        }
      } catch (err) {
        console.error(err);
      } finally {
        btnSia.textContent = "Générer Rapport SIA 118";
        btnSia.disabled = false;
      }
    });

    // Export PDF button (SIA 118 Bautagebuch & Regierapport)
    const btnExportPdf = document.getElementById('btn-export-pdf');
    btnExportPdf?.addEventListener('click', async () => {
      if (!this.lastBautagebuchResponse) {
        alert("Veuillez d'abord générer un rapport Bautagebuch.");
        return;
      }
      btnExportPdf.textContent = "⏳ Génération PDF...";
      btnExportPdf.disabled = true;

      try {
        const res = await fetch('/api/copilot/bautagebuch/export-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.lastBautagebuchResponse)
        });
        if (!res.ok) throw new Error("Erreur export PDF");
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Bautagebuch_SIA118_${this.lastBautagebuchResponse.date || 'Rapport'}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      } catch (err) {
        console.error("PDF export error:", err);
        alert("Erreur lors de la génération du PDF.");
      } finally {
        btnExportPdf.textContent = "📄 Exporter Bautagebuch & Regie PDF (SIA 118)";
        btnExportPdf.disabled = false;
      }
    });

    // Pin on map button
    document.getElementById('btn-pin-on-map')?.addEventListener('click', () => {
      const coords = [8.7687, 46.6660]; // Gotthard Base Tunnel PK 220.975 (Querschlag QS-42)
      this.map.flyTo({ center: coords, zoom: 18, pitch: 50 });

      if (this.incidentMarker) this.incidentMarker.remove();

      const el = document.createElement('div');
      el.style.cssText = 'background:#ff334b; width:22px; height:22px; border-radius:50%; border:3px solid white; box-shadow:0 0 15px #ff334b; animation:pulse-dot 1.2s infinite; cursor:pointer;';
      
      this.incidentMarker = new maplibregl.Marker({ element: el })
        .setLngLat(coords)
        .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML('<strong>⚠️ ALERTE PK 220.975 (QS-42)</strong><br>Rupture conduite drainage & Regierapport SIA 118 Art. 44'))
        .addTo(this.map);
    });

    // Multimodal Visual Inspection scenarios
    const scenarioData = {
      fouille: {
        img: '/demo/images/trench_hazard.svg',
        desc: "Tranchée d'excavation de 2m60 de profondeur creusée dans le remblai sans blindage ni caisson. Ouvriers au fond sans échappatoire."
      },
      echafaudage: {
        img: '/demo/images/scaffold_hazard.svg',
        desc: "Échafaudage métallique de façade de 3m20 sans garde-corps supérieur ni plinthe. Ouvriers en hauteur sans ligne de vie (BauAV Art. 15)."
      },
      roche: {
        img: '/demo/images/rockface_hazard.svg',
        desc: "Front de taille et voûte d'excavation souterraine présentant une fissuration active avec venues d'eau sans ancrage ni boulons d'ancrage (SIA 198)."
      },
      ventilation: {
        img: '/demo/images/rockface_hazard.svg',
        desc: "Arrêt de la ventilation secondaire dans la galerie d'avancement. Taux de monoxyde de carbone (CO) mesuré à 45 ppm avec engins diesel en marche (SIA 196)."
      }
    };

    const selScenario = document.getElementById('sel-suva-scenario');
    const imgPreview = document.getElementById('img-suva-preview');
    const txtSuvaDesc = document.getElementById('txt-suva-desc');
    const scenarioBtns = document.querySelectorAll('#suva-image-container .ctrl-btn-sm');

    const updateScenarioUI = (key) => {
      const item = scenarioData[key];
      if (!item) return;
      if (imgPreview) imgPreview.src = item.img;
      if (txtSuvaDesc) txtSuvaDesc.value = item.desc;
      scenarioBtns.forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-scenario') === key);
      });
      if (selScenario && selScenario.value !== key) {
        selScenario.value = key;
      }
    };

    selScenario?.addEventListener('change', (e) => {
      updateScenarioUI(e.target.value);
    });

    scenarioBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-scenario');
        updateScenarioUI(key);
      });
    });

    // Run SUVA audit button
    const btnSuva = document.getElementById('btn-run-suva-audit');
    btnSuva?.addEventListener('click', async () => {
      btnSuva.textContent = "⚡ Analyse Réglementaire SUVA...";
      btnSuva.disabled = true;

      const desc = document.getElementById('txt-suva-desc').value;

      try {
        const res = await fetch('/api/copilot/suva-audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: desc })
        });
        const data = await res.json();

        const card = document.getElementById('card-suva-result');
        const pre = document.getElementById('pre-suva-output');
        const badge = document.getElementById('badge-suva-status');

        card.classList.remove('hidden');
        badge.textContent = data.stop_work_order ? "DANGER VITAL — STOPP SUVA" : "CONFORME";
        badge.className = `result-badge ${data.stop_work_order ? 'danger' : 'compliant'}`;

        let text = `${data.diagnostic_fr}\n\n`;
        text += "--- RÈGLES ENFREINTES ---\n";
        data.infracted_rules.forEach(r => {
          text += `• [${r.norm}] ${r.title}\n  Action : ${r.corrective_action}\n`;
        });

        pre.textContent = text;
      } catch (err) {
        console.error(err);
      } finally {
        btnSuva.textContent = "⚡ Lancer Audit Sécurité SUVA";
        btnSuva.disabled = false;
      }
    });
  }

  setupStrategicEvents() {
    // ── Sliders Readout ──────────────────────────────────────────
    const syncSlider = (id, valId) => {
      const slider = document.getElementById(id);
      const val = document.getElementById(valId);
      slider?.addEventListener('input', (e) => {
        if (val) val.textContent = `${e.target.value}%`;
      });
    };
    syncSlider('slider-w-opp', 'val-w-opp');
    syncSlider('slider-w-cost', 'val-w-cost');
    syncSlider('slider-w-env', 'val-w-env');
    syncSlider('slider-w-dur', 'val-w-dur');

    // ── Infrastructure Siting & Placement Presets ───────────────
    const infraPresets = {
      'scen-contournement': {
        name: "Contournement Cantonal & Desserte Régionale",
        loc: "Valais / Vaud",
        variants: [
          {
            id: "var_nord",
            name: "Tracé Nord (Crête & Semi-enterré)",
            location_name: "Crête Nord (Contournement)",
            coordinates: [8.7850, 46.6740],
            proximity_to_housing_m: 950,
            zoning_type: "Zone forestière & sous-sol",
            type: "corridor",
            estimated_cost_chf: 54000000.0,
            estimated_duration_months: 28,
            description: "Tracé en hauteur éloigné des agglomérations. Zéro dépassement de bruit OPB, acceptabilité maximale."
          },
          {
            id: "var_median",
            name: "Tracé Médian (Plateau Agricole)",
            location_name: "Plateau d'Ergisch",
            coordinates: [8.7730, 46.6680],
            proximity_to_housing_m: 420,
            zoning_type: "Zone agricole protégée (SDA Art. 15)",
            type: "surface",
            estimated_cost_chf: 38000000.0,
            estimated_duration_months: 26,
            description: "Tracé en pente douce mais touchant des terres d'assolement SDA protégées par la LAT."
          },
          {
            id: "var_sud",
            name: "Tracé Sud (Fond de Vallée)",
            location_name: "Fond de Vallée Résidentiel",
            coordinates: [8.7610, 46.6620],
            proximity_to_housing_m: 130,
            zoning_type: "Zone résidentielle dense & mixte",
            type: "surface",
            estimated_cost_chf: 26000000.0,
            estimated_duration_months: 20,
            description: "Tracé économique immédiat longeant les habitations. Risque maximal d'oppositions OPB Art. 7."
          }
        ]
      },
      'scen-plateforme': {
        name: "Plateforme Logistique Multimodale & Portail",
        loc: "Vaud (Plaine du Rhône)",
        variants: [
          {
            id: "var_zi",
            name: "Emplacement A (Zone Industrielle)",
            location_name: "Zone Industrielle En Bovey",
            coordinates: [8.7520, 46.6550],
            proximity_to_housing_m: 800,
            zoning_type: "Zone industrielle & activités",
            type: "site",
            estimated_cost_chf: 32000000.0,
            estimated_duration_months: 18,
            description: "Raccordement ferroviaire existant, compatibilité totale LAT, absence de litiges riverains."
          },
          {
            id: "var_sda",
            name: "Emplacement B (Plaine Agricole SDA)",
            location_name: "Plaine Alluviale",
            coordinates: [8.7640, 46.6600],
            proximity_to_housing_m: 350,
            zoning_type: "Surfaces d'assolement (SDA)",
            type: "site",
            estimated_cost_chf: 24000000.0,
            estimated_duration_months: 24,
            description: "Coût d'acquisition attractif mais opposition de l'Union des paysans pour perte de quota SDA."
          },
          {
            id: "var_village",
            name: "Emplacement C (Périphérie Village)",
            location_name: "Entrée Ouest Village",
            coordinates: [8.7780, 46.6700],
            proximity_to_housing_m: 160,
            zoning_type: "Zone mixte artisanat / habitat",
            type: "site",
            estimated_cost_chf: 27000000.0,
            estimated_duration_months: 28,
            description: "Conflit direct avec les riverains pour nuisances de trafic de camions (OPB / CC 679/684)."
          }
        ]
      },
      'scen-alpin': {
        name: "Liaison Traversée de la Vallée Alpine",
        loc: "Valais / Uri",
        variants: [
          {
            id: "var_tunnel",
            name: "Tracé Souterrain (Tunnel de Base)",
            location_name: "Massif Alpin Souterrain",
            coordinates: [8.7650, 46.6610],
            proximity_to_housing_m: 900,
            zoning_type: "Sous-sol rocheux",
            type: "tunnel",
            estimated_cost_chf: 78000000.0,
            estimated_duration_months: 36,
            description: "Ouvrage foré sous la roche. Zéro nuisance sonore de surface, protection intégrale ISOS."
          },
          {
            id: "var_bridge",
            name: "Tracé Aérien (Grand Viaduc)",
            location_name: "Franchissement Aérien Crêtes",
            coordinates: [8.7750, 46.6720],
            proximity_to_housing_m: 220,
            zoning_type: "Site paysager protégé (ISOS)",
            type: "bridge",
            estimated_cost_chf: 42000000.0,
            estimated_duration_months: 28,
            description: "Grand viaduc métallique aérien exposé aux recours paysagers associatifs (ISOS/OPB)."
          }
        ]
      }
    };

    const renderVariantCards = (variants) => {
      const container = document.getElementById('infra-variants-container');
      if (!container) return;
      container.innerHTML = variants.map((v, i) => {
        const colors = ['#38bdf8', '#fbbf24', '#f87171', '#34d399'];
        const col = colors[i % colors.length];
        return `
          <div class="bid-card" style="margin-bottom:8px; border-left:3px solid ${col};">
            <div style="display:flex; justify-content:space-between; font-weight:700; color:${col};">
              <span>📍 ${v.name}</span>
              <span>${v.estimated_cost_chf.toLocaleString('fr-CH')} CHF</span>
            </div>
            <div style="font-size:10px; color:#cbd5e1; margin-top:2px; display:flex; gap:10px;">
              <span>Site: <b>${v.location_name || 'N/A'}</b></span>
              <span>Habitations: <b>${v.proximity_to_housing_m}m</b></span>
              <span>Zone: <b>${v.zoning_type}</b></span>
            </div>
            <div style="font-size:10px; color:var(--text-secondary); margin-top:3px; line-height:1.3;">
              Durée: ${v.estimated_duration_months} mois · ${v.description}
            </div>
          </div>
        `;
      }).join('');
    };

    const selInfraScen = document.getElementById('sel-infra-scenario');
    const updateScenarioUI = () => {
      const scenKey = selInfraScen?.value || 'scen-contournement';
      const p = infraPresets[scenKey] || infraPresets['scen-contournement'];
      if (!p) return;
      document.getElementById('txt-project-name').value = p.name;
      document.getElementById('txt-project-loc').value = p.loc;
      renderVariantCards(p.variants);
    };

    selInfraScen?.addEventListener('change', updateScenarioUI);
    // Initial populate
    updateScenarioUI();

    // ── Run Siting Arbitrage ─────────────────────────────────────
    const btnArbitrage = document.getElementById('btn-run-arbitrage');
    btnArbitrage?.addEventListener('click', async () => {
      btnArbitrage.textContent = "⚡ Calcul de l'Emplacement Optimal (Apertus)...";
      btnArbitrage.disabled = true;

      const scenKey = document.getElementById('sel-infra-scenario').value;
      const preset = infraPresets[scenKey] || infraPresets['scen-contournement'];
      const projName = document.getElementById('txt-project-name').value;
      const projLoc = document.getElementById('txt-project-loc').value;

      const wOpp = parseFloat(document.getElementById('slider-w-opp').value) / 100;
      const wCost = parseFloat(document.getElementById('slider-w-cost').value) / 100;
      const wEnv = parseFloat(document.getElementById('slider-w-env').value) / 100;
      const wDur = parseFloat(document.getElementById('slider-w-dur').value) / 100;

      const payload = {
        project_name: projName,
        location: projLoc,
        variants: preset.variants,
        priorities: {
          cost: wCost,
          opposition_risk: wOpp,
          environmental_impact: wEnv,
          duration: wDur
        }
      };

      try {
        const res = await fetch('/api/project/infrastructure-arbitration', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        this.lastArbitrageResponse = data;

        const card = document.getElementById('card-arbitrage-result');
        card.classList.remove('hidden');

        document.getElementById('txt-arbitrage-winner').textContent = data.recommended_variant;
        const optLocEl = document.getElementById('txt-arbitrage-optimal-loc');
        if (optLocEl) {
          optLocEl.textContent = data.optimal_location_name ? `📍 Emplacement Retenu : ${data.optimal_location_name}` : '';
        }
        document.getElementById('txt-arbitrage-summary-fr').textContent = data.decision_summary_fr;
        const tradeoffEl = document.getElementById('txt-arbitrage-tradeoff');
        if (tradeoffEl) {
          tradeoffEl.textContent = data.siting_tradeoff_analysis_fr || '';
        }

        // Populate table
        const tbody = document.getElementById('tbody-arbitrage-eval');
        tbody.innerHTML = '';
        data.evaluations.forEach(ev => {
          const matchingVar = preset.variants.find(v => v.id === ev.variant_id || v.name === ev.variant_name);
          const tr = document.createElement('tr');
          const isWinner = ev.variant_name === data.recommended_variant || ev.variant_id === data.recommended_variant;
          tr.style.background = isWinner ? 'rgba(0, 230, 118, 0.12)' : 'transparent';
          const oppColor = ev.opposition_risk_level === 'Faible' ? '#00e676' : (ev.opposition_risk_level === 'Moyen' ? '#ffb74d' : '#ff5252');
          
          tr.innerHTML = `
            <td><b>${ev.variant_name}</b><br><small style="color:#94a3b8;">${ev.location_name || ''}</small></td>
            <td><small style="color:#38bdf8;">${matchingVar?.zoning_type || 'Zone mixte'}</small><br><small>${matchingVar?.proximity_to_housing_m || 500}m hab.</small></td>
            <td>${ev.cost_score}/100</td>
            <td><span style="color:${oppColor}; font-weight:700;">${ev.opposition_risk_level}</span></td>
            <td>${ev.estimated_litigation_delay_months} m.</td>
            <td>${ev.environmental_score}/100</td>
            <td><b style="color:${isWinner ? '#00e676' : '#fff'}; font-size:12px;">${ev.total_score} pts</b></td>
          `;
          tbody.appendChild(tr);
        });

        // Legal list
        const legalDiv = document.getElementById('list-arbitrage-legal');
        legalDiv.innerHTML = data.swiss_legal_basis.map(l => `• ${l}`).join('<br/>');

        // Automatically display markers on map
        this.displayArbitrageOnMap(data, preset.variants);

      } catch (err) {
        console.error("Arbitrage error:", err);
      } finally {
        btnArbitrage.textContent = "⚡ Trouver l'Emplacement Optimal (Apertus v1.5-70B)";
        btnArbitrage.disabled = false;
      }
    });

    // Method to display markers on map
    this.displayArbitrageOnMap = (data, variants) => {
      if (!this.map || !data) return;
      this.arbitrageMarkers.forEach(m => m.remove());
      this.arbitrageMarkers = [];

      let winnerCoords = data.optimal_coordinates || [8.7850, 46.6740];

      data.evaluations.forEach(ev => {
        const vConfig = variants.find(v => v.id === ev.variant_id || v.name === ev.variant_name);
        const coords = ev.coordinates || vConfig?.coordinates || [8.7690, 46.6660];
        const isWinner = ev.variant_name === data.recommended_variant || ev.variant_id === data.recommended_variant;

        if (isWinner && ev.coordinates) {
          winnerCoords = ev.coordinates;
        }

        const el = document.createElement('div');
        if (isWinner) {
          el.style.cssText = 'background:#00e676; width:34px; height:34px; border-radius:50%; border:3px solid white; box-shadow:0 0 22px #00e676; display:flex; align-items:center; justify-content:center; color:#000; font-weight:900; font-size:14px; cursor:pointer; animation:pulse 2s infinite;';
          el.textContent = '🏆';
        } else {
          el.style.cssText = 'background:#f59e0b; width:26px; height:26px; border-radius:50%; border:2px solid white; box-shadow:0 0 10px #f59e0b; display:flex; align-items:center; justify-content:center; color:#000; font-weight:800; font-size:11px; cursor:pointer;';
          el.textContent = '📍';
        }

        const popupHtml = isWinner ? `
          <div style="font-family:sans-serif; min-width:210px;">
            <div style="background:#00e676; color:#000; padding:4px 6px; font-weight:800; font-size:11px; border-radius:3px; margin-bottom:4px;">
              🏆 POSITION OPTIMALE RETENUE
            </div>
            <strong>${ev.variant_name}</strong><br/>
            <b>Site :</b> ${ev.location_name || 'N/A'}<br/>
            <b>Score Global :</b> <span style="color:#00e676; font-weight:700;">${ev.total_score} pts</span><br/>
            <b>Risque Oppositions :</b> <span style="color:#00e676; font-weight:700;">${ev.opposition_risk_level}</span> (${ev.estimated_litigation_delay_months} m. recours)<br/>
            <b>Habitations :</b> ${vConfig?.proximity_to_housing_m || 500}m · <b>Zone LAT :</b> ${vConfig?.zoning_type || 'Mixte'}<br/>
            <div style="margin-top:4px; font-size:10px; color:#64748b; font-style:italic;">
              Sélectionné pour la meilleure conciliation des 4 piliers (oppositions, coûts, délais, impact).
            </div>
          </div>
        ` : `
          <div style="font-family:sans-serif; min-width:200px;">
            <div style="background:#f59e0b; color:#000; padding:3px 6px; font-weight:700; font-size:10px; border-radius:3px; margin-bottom:4px;">
              📍 SITE CANDIDAT ÉVALUÉ
            </div>
            <strong>${ev.variant_name}</strong><br/>
            <b>Site :</b> ${ev.location_name || 'N/A'}<br/>
            <b>Score Global :</b> ${ev.total_score} pts<br/>
            <b>Risque Oppositions :</b> <span style="color:#ff5252; font-weight:700;">${ev.opposition_risk_level}</span> (${ev.estimated_litigation_delay_months} mois de recours)<br/>
            <b>Habitations :</b> ${vConfig?.proximity_to_housing_m || 500}m · <b>Zone :</b> ${vConfig?.zoning_type || 'Mixte'}
          </div>
        `;

        const popup = new maplibregl.Popup({ offset: 25 }).setHTML(popupHtml);
        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .setPopup(popup)
          .addTo(this.map);

        if (isWinner) {
          popup.addTo(this.map);
        }

        this.arbitrageMarkers.push(marker);
      });

      this.map.flyTo({
        center: winnerCoords,
        zoom: 14.5,
        pitch: 50,
        bearing: -15
      });
    };

    // ── Export Arbitrage PDF ─────────────────────────────────────
    const btnExportArbPdf = document.getElementById('btn-export-arbitrage-pdf');
    btnExportArbPdf?.addEventListener('click', async () => {
      if (!this.lastArbitrageResponse) {
        alert("Veuillez d'abord exécuter l'arbitrage.");
        return;
      }
      btnExportArbPdf.textContent = "⏳ Génération PDF...";
      btnExportArbPdf.disabled = true;

      try {
        const res = await fetch('/api/project/export-decision-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.lastArbitrageResponse)
        });
        if (!res.ok) throw new Error("Erreur export PDF");
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeName = (this.lastArbitrageResponse.project_name || 'Projet').replace(/\s+/g, '_');
        a.download = `Optimisation_Emplacement_${safeName}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      } catch (err) {
        console.error("PDF export error:", err);
        alert("Erreur lors de la génération du PDF décisionnel.");
      } finally {
        btnExportArbPdf.textContent = "📄 Exporter Rapport d'Implantation A4 (PDF)";
        btnExportArbPdf.disabled = false;
      }
    });

    // ── Map Arbitrage Visualizer ─────────────────────────────────
    document.getElementById('btn-map-arbitrage')?.addEventListener('click', () => {
      const scenKey = document.getElementById('sel-infra-scenario')?.value || 'scen-contournement';
      const preset = infraPresets[scenKey] || infraPresets['scen-contournement'];
      if (this.lastArbitrageResponse) {
        this.displayArbitrageOnMap(this.lastArbitrageResponse, preset.variants);
      } else {
        alert("Veuillez d'abord lancer l'arbitrage pour calculer la position optimale.");
      }
    });

    // ── Run Tender Comparison (SIA 118 / AIMP) ───────────────────
    const btnTender = document.getElementById('btn-run-tender');
    btnTender?.addEventListener('click', async () => {
      btnTender.textContent = "⚡ Analyse AIMP / SIA 118 en cours...";
      btnTender.disabled = true;

      const payload = {
        lot_name: document.getElementById('txt-tender-lot').value,
        owner_estimate_chf: parseFloat(document.getElementById('txt-tender-estimate').value),
        bids: [
          {
            contractor_name: "SwissTunnel Bau AG",
            total_price_chf: 1485000.0,
            duration_months: 18,
            experience_rating: 5,
            has_subcontractors: false,
            unforeseen_exclusion_clauses: []
          },
          {
            contractor_name: "LowCost Excavations Sàrl",
            total_price_chf: 980000.0,
            duration_months: 14,
            experience_rating: 2,
            has_subcontractors: true,
            unforeseen_exclusion_clauses: ["Exclusion de garantie en cas d'infiltrations d'eau ou aléas géologiques"]
          },
          {
            contractor_name: "Implenia Infra SA",
            total_price_chf: 1580000.0,
            duration_months: 20,
            experience_rating: 5,
            has_subcontractors: true,
            unforeseen_exclusion_clauses: []
          }
        ]
      };

      try {
        const res = await fetch('/api/project/tender-comparison', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        const card = document.getElementById('card-tender-result');
        card.classList.remove('hidden');

        document.getElementById('txt-tender-winner').textContent = data.awarded_contractor;
        document.getElementById('txt-tender-rationale-fr').textContent = data.award_rationale_fr;

        // Flags
        const flagsDiv = document.getElementById('list-tender-flags');
        flagsDiv.innerHTML = '';
        data.bids_analysis.forEach(b => {
          if (b.is_abnormally_low || b.hidden_risk_flags.length > 0) {
            const flagBox = document.createElement('div');
            flagBox.className = `risk-flag ${b.is_abnormally_low ? 'danger' : ''}`;
            flagBox.innerHTML = `<b>${b.contractor_name}</b> : ${b.hidden_risk_flags.join(' · ')}`;
            flagsDiv.appendChild(flagBox);
          }
        });

        // Recommendations
        const clausesDiv = document.getElementById('list-tender-clauses');
        clausesDiv.innerHTML = data.contractual_recommendations.map(c => `• ${c}`).join('<br/>');

      } catch (err) {
        console.error("Tender error:", err);
      } finally {
        btnTender.textContent = "⚡ Analyser les Offres (SIA 118 / AIMP)";
        btnTender.disabled = false;
      }
    });

    // ── Run Permit Opposition (LAT / OPB) ────────────────────────
    const oppPresets = {
      'opp-1': "Nous formons opposition formelle contre le projet. Le passage continu de camions et le bruit assourdissant du concassage de nuit violent l'Ordonnance sur la protection contre le bruit (OPB RS 814.41). De plus, la hauteur du silo de ventilation de 18 mètres dépasse le gabarit communal et prive nos chalets d'ensoleillement selon l'art. 679/684 CC.",
      'opp-2': "En tant qu'association de protection de la nature et du patrimoine, nous nous opposons à l'implantation du portail qui défigure le site protégé à l'ISOS (Inventaire fédéral des sites construits d'importance nationale) et réclamons un plan d'évacuation des déblais par rail selon la LPE Art. 30.",
      'opp-3': "Notre collectif de riverains et d'agriculteurs conteste l'accès de chantier par le chemin vicinal. La circulation de 120 poids lourds par jour menace la sécurité des enfants du village et viole la Loi fédérale sur la circulation routière (LCR)."
    };

    const selOppPreset = document.getElementById('sel-opp-preset');
    selOppPreset?.addEventListener('change', (e) => {
      const text = oppPresets[e.target.value];
      if (text) document.getElementById('txt-opp-text').value = text;
    });

    const btnOpp = document.getElementById('btn-run-opposition');
    btnOpp?.addEventListener('click', async () => {
      btnOpp.textContent = "⚡ Qualification Juridique en cours...";
      btnOpp.disabled = true;

      const payload = {
        project_title: document.getElementById('txt-opp-project').value,
        project_location: document.getElementById('txt-opp-loc').value,
        opposition_raw_text: document.getElementById('txt-opp-text').value,
        inquiry_deadline_days: 30
      };

      try {
        const res = await fetch('/api/project/permit-opposition', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        const card = document.getElementById('card-opposition-result');
        card.classList.remove('hidden');

        document.getElementById('txt-opp-validity').textContent = `Statut : ${data.opposition_validity}`;
        document.getElementById('txt-opp-delay').textContent = `⏱️ Délai estimé de la procédure de conciliation / recours : ~${data.estimated_delay_weeks} semaines`;

        // Grievances
        const listDiv = document.getElementById('list-opp-grievances');
        listDiv.innerHTML = '';
        data.grievances.forEach(g => {
          const gBox = document.createElement('div');
          gBox.className = 'bid-card';
          gBox.style.marginBottom = '6px';
          gBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; font-weight:700; color:#38bdf8;">
              <span>• ${g.category} (Sévérité: ${g.severity})</span>
              <span style="font-family:var(--font-mono); font-size:10px; color:#f59e0b;">${g.legal_basis}</span>
            </div>
            <div style="font-size:10px; color:#cbd5e1; margin-top:3px;"><b>Grief :</b> ${g.claim_summary}</div>
            <div style="font-size:10px; color:#a7f3d0; margin-top:2px;"><b>Réfutation & Remédiation :</b> ${g.rebuttal_strategy}</div>
          `;
          listDiv.appendChild(gBox);
        });

        // Letter
        document.getElementById('txt-opp-letter-fr').textContent = data.draft_rebuttal_letter_fr;

      } catch (err) {
        console.error("Opposition error:", err);
      } finally {
        btnOpp.textContent = "⚡ Qualifier les Griefs & Générer Réfutation";
        btnOpp.disabled = false;
      }
    });
  }
}

// Bootstrap
window.addEventListener('DOMContentLoaded', () => {
  const app = new ChronoMineApp();
  app.init();
});
