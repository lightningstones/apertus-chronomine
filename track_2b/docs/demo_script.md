# ChronoMine AI — Script Démo Vidéo (2 Minutes Max)
**Hack Apertus 2026 — Track 2B: Subterranean Sovereign Copilot**

Ce script est conçu pour enregistrer la vidéo de démonstration de 2 minutes requise pour la soumission Hack Apertus.

---

### Timing & Découpage Visuel

| Temps | Visuel à l'écran | Voix-off / Narration (FR ou EN) |
|---|---|---|
| **0:00 - 0:25** | **Introduction & Problème**<br>- Vue 3D du chantier souterrain (tunnel & mineurs géolocalisés).<br>- Rappel des contraintes suisses : chantiers confinés, sans internet (Air-gapped), sécurité SUVA vitale. | *« En Suisse, les chantiers souterrains comme les cavernes RUAG et les galeries du Saint-Gothard opèrent sous des contraintes extrêmes : aucune connectivité externe (air-gapped), une main-d'œuvre internationale (portugais, italien, espagnol) et une responsabilité juridique stricte sous les normes SIA 118 et SUVA BauAV. Voici ChronoMine AI, le premier copilote souverain propulsé par Apertus v1.5. »* |
| **0:25 - 1:00** | **Cas 1 : Journal de Chantier Multilingue & SIA 118**<br>- Clic sur le bouton d'exemple Portugais (*A escavadora partiu uma tubagem no PK 3.200...*).<br>- Sélection de la langue de sortie : Allemand (norme suisse).<br>- Clic sur **"Générer Bautagebuch (Apertus)"**.<br>- Résultat instantané affiché à droite avec métadonnées extraites. | *« Un chef de poste saisit ou dicte une note brute en portugais : bris de conduite de drainage, 3 ouvriers mobilisés, 2h30 d'arrêt. En un clic, Apertus v1.5 traduit et structure la note en un Bautagebuch officiel allemand, extrait les heures d'arrêt, et génère automatiquement le Regierapport selon l'Article 44 de la norme SIA 118 pour sécuriser la facturation des travaux en régie. »* |
| **1:00 - 1:35** | **Cas 2 : Audit de Sécurité & Prévention SUVA**<br>- Bascule sur l'onglet **"Audit Sécurité SUVA"**.<br>- Chargement du cas critique (fouille de 2m60 sans blindage).<br>- Lancement de l'audit Apertus.<br>- Alerte rouge instantanée : **ARRÊT DE TRAVAIL IMMÉDIAT (Stop-Work Order)**, référence légale BauAV Art. 54, actions correctives. | *« Deuxième pilier : la vie des mineurs et la conformité SUVA. Face au signalement d'une fouille non sécurisée de 2m60, Apertus analyse la situation contre la base légale de l'ordonnance BauAV 2022. Le modèle déclenche immédiatement un ordre d'arrêt de travail obligatoire, cite l'article 54, et dicte les mesures de blindage d'urgence avant tout accident mortel. »* |
| **1:35 - 2:00** | **Conclusion & Souveraineté Suisse**<br>- Affichage de l'indicateur "Air-gapped Sovereign Node" (100% On-premise / Cloud CSCS Suisse).<br>- Présentation du dataset Hugging Face et du rapport technique. | *« ChronoMine AI fonctionne à 100% en local et en réseau isolé (Air-gapped) sur serveur de chantier ou sur le cloud souverain suisse CSCS avec Apertus v1.5-8B et 70B. Zéro fuite de données, totale conformité helvétique, sécurité maximale pour nos infrastructures critiques. »* |

---

### Checklist Pré-Enregistrement
1. [ ] Lancer l'application : `make run` ou `.venv\Scripts\python.exe -m uvicorn src.backend.main:app --app-dir track_2b --port 8000`
2. [ ] Ouvrir le navigateur en plein écran sur `http://localhost:8000`
3. [ ] Avoir les notes de démonstration prêtes (les boutons d'exemples dans l'interface pré-remplissent automatiquement les formulaires)
4. [ ] Outil de capture d'écran : OBS Studio, Windows Game Bar (Win+G), ou Loom
5. [ ] Durée cible : **1 minute 50 secondes** (pour être confortablement sous les 2 minutes réglementaires).
