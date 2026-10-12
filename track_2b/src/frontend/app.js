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
    this.is3D = false;
    this.lastBautagebuchResponse = null;
  }

  async init() {
    this.setupClock();
    this.setupTabs();
    this.setupCopilotEvents();
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
}

// Bootstrap
window.addEventListener('DOMContentLoaded', () => {
  const app = new ChronoMineApp();
  app.init();
});
