# trend-driven-category-system

Demand-driven infrastructure analysis system using Google Trends data, FastAPI, PostgreSQL and Docker.

---

# Project Structure

```text
app/
├── api/
├── services/
├── engines/
├── schemas/
├── db/
├── clients/
└── core/

config/
data/
├── raw/
└── processed/

frontend/
scripts/

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

# Technology Stack

* Python 3.11+
* FastAPI
* PostgreSQL 15
* Docker / Docker Compose
* Pandas
* Pytrends
* SQLAlchemy
* Uvicorn

---

# Requirements

Recommended environment:

* Windows 11
* WSL2
* Ubuntu 24.04
* Docker Desktop with WSL integration enabled

---

# Getting Started

## 1. Clone repository

```bash
git clone https://github.com/nagyosse/trend-driven-category-system.git
cd trend-driven-category-system
```

---

## 2. Create environment file

```bash
cp .env.example .env
```

---

## 3. Start services

```bash
docker compose up --build
```

Services:

| Service    | Port |
| ---------- | ---- |
| FastAPI    | 8000 |
| PostgreSQL | 5432 |

---

# Verify Running Services

## Docker containers

```bash
docker ps
```

Expected containers:

* trend_api
* trend_db

---

## API health check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"ok"}
```

---

## Swagger UI

Open in browser:

```text
http://localhost:8000/docs
```

---

# Database Initialization

After first startup, initialize database tables:

```bash
docker exec -it trend_api bash
python scripts/bootstrap_db.py
exit
```

Expected output:

```text
Adatbázis táblák létrehozva.
```

---

# Frontend

Start frontend locally:

```bash
cd frontend
python3 -m http.server 5500
```

Open in browser:

```text
http://localhost:5500
```

---

# Run Analysis Test

Example API request:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "IPO frontend teszt",
    "ai_enabled": false,
    "run_trends_fetch": true,
    "categories": [
      {
        "category_id": "notebooks",
        "category_name": "Notebookok",
        "keywords": ["notebook", "laptop"]
      },
      {
        "category_id": "components",
        "category_name": "Komponensek",
        "keywords": ["ssd", "ram"]
      }
    ]
  }'
```

---

# Generated Files

Raw trend data:

```text
data/raw/trends_long.csv
```

Processed files:

```text
data/processed/category_weekly_index.csv
data/processed/category_summary.csv
data/processed/category_ranking.csv
```

---

# Ranking Endpoint

```bash
curl http://localhost:8000/api/v1/ranking
```

Example response:

```json
{
  "items": [
    {
      "final_rank": 1,
      "category_id": "notebooks",
      "category_name": "Notebookok"
    }
  ]
}
```

---

# Useful Commands

## Show logs

```bash
docker compose logs -f
```

## Stop services

```bash
docker compose down
```

## Rebuild containers

```bash
docker compose up --build
```

## Enter API container

```bash
docker exec -it trend_api bash
```

---

# Development Notes

If generated files are owned by root:

```bash
sudo chown -R $USER:$USER data
```

---

# API Endpoints

| Endpoint                   | Method | Description          |
| -------------------------- | ------ | -------------------- |
| /api/v1/health             | GET    | Health check         |
| /api/v1/ranking            | GET    | Get category ranking |
| /api/v1/analyze            | POST   | Run trend analysis   |
| /api/v1/ai/explain-ranking | POST   | AI explanation       |

---

# Current Status

```text
 Dockerized backend
 PostgreSQL integration
 Google Trends processing
 Category aggregation
 Ranking engine
 REST API
 Frontend prototype
```
