# Google Maps Lead Intelligence

Application FastAPI de lead intelligence basée sur le scraping Google Maps.  
Déployable sur Railway avec un lien public, sans API Google.

---

## Objectif

Identifier et prioriser des établissements à fort potentiel commercial en analysant leurs avis Google Maps : notes faibles, mots-clés négatifs, volume d'avis. Chaque lead est scoré et un angle commercial est automatiquement suggéré.

---

## Stack

| Composant | Technologie |
|-----------|-------------|
| Backend   | FastAPI + Uvicorn |
| Scraping  | Playwright (Chromium headless) |
| Base de données | SQLite |
| Frontend  | Jinja2 + CSS vanilla |
| Déploiement | Railway (Docker) |

---

## Architecture

```
google-maps-lead-intelligence/          ← racine git / Dockerfile
├── requirements.txt
├── Dockerfile
├── railway.json
└── google-maps-lead-intelligence/      ← code applicatif
    ├── app/
    │   ├── main.py       ← FastAPI, routes
    │   ├── database.py   ← SQLite CRUD
    │   ├── analytics.py  ← scoring, mots-clés, analytics
    │   └── scraper.py    ← Playwright Google Maps
    ├── templates/
    │   └── index.html    ← dashboard Jinja2
    └── static/
        └── style.css
```

---

## Lancement local

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Installer Chromium pour Playwright
playwright install chromium

# 3. Lancer l'app (depuis le dossier inner)
cd google-maps-lead-intelligence
python -m uvicorn app.main:app --reload --port 8002
```

Ouvrir : http://localhost:8002

---

## Déploiement Railway

```bash
# 1. Se connecter à Railway CLI
railway login

# 2. Initialiser le projet (depuis la racine git)
railway init

# 3. Déployer
railway up
```

Ou via l'interface Railway :
1. New Project → Deploy from GitHub repo
2. Railway détecte le Dockerfile automatiquement
3. L'URL publique est générée automatiquement

---

## Scoring commercial

| Critère | Points |
|---------|--------|
| Note < 3.8 | +30 |
| Plus de 100 avis | +20 |
| Mots-clés négatifs détectés | +25 |
| Téléphone présent | +10 |
| Site web présent | +10 |

**Labels :** High (70+) · Medium (40–69) · Low (<40)

---

## Valeur business

- Identifier des établissements avec une réputation dégradée = opportunité de vente de services (gestion d'avis, formation, refonte site, communication…)
- Vue cross-industrie pour comparer les secteurs
- Angle commercial pré-rempli pour chaque lead
- Dashboard public partageable avec toute l'équipe commerciale
