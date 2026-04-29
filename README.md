# Trend-Driven Category System

A demand-driven infrastructure control system that uses Google Trends data to dynamically analyze product categories and support scaling decisions in a containerized (Docker/Swarm) environment.

---

##  Project Goal

The goal of the system is to demonstrate a **data-driven decision support model**, where:

- external search demand (Google Trends)  
- is transformed into measurable indicators  
- which drive infrastructure and business decisions  

The system follows a **deterministic and reproducible pipeline**, ensuring that identical inputs always produce identical outputs.

---

##  Core Concept (IPO Model)

The system is built around the **Input → Process → Output (IPO)** model.

### Input
- User-defined categories
- Keywords (max. 4 per category)
- Optional AI interpretation
- Optional live Google Trends data fetch

### Process
- Google Trends data aggregation
- Weekly normalization and smoothing
- Category-level demand index calculation
- Ranking algorithm (deterministic)
- Optional AI-based explanation

### Output
- Ranked category list
- Statistical indicators:
  - 53-week average
  - Last 8-week average
  - Peak value
  - Active weeks
- AI-generated business summary (optional)
- Docker Swarm scaling recommendation

---

##  Features

-  Google Trends data processing
-  Category-based demand ranking
-  Optional AI interpretation (OpenAI)
-  Docker-based deployment
-  PostgreSQL logging (full pipeline traceability)
-  Simple web frontend
-  Fully reproducible execution
-  Exportable scaling configuration

---

##  System Architecture
### Components

| Layer      | Description |
|------------|------------|
| Frontend   | User interface (input + visualization) |
| API        | FastAPI endpoints |
| Services   | Business logic (pipeline orchestration) |
| Engines    | Deterministic calculations |
| Database   | Logging & traceability |
| External   | Google Trends + OpenAI |

---

## Project Structure

app/
api/
services/
engines/
schemas/
db/
clients/
core/

config/
data/
raw/
processed/

frontend/
scripts/

Dockerfile
docker-compose.yml
requirements.txt

---

## Getting Started

### 1. Clone repository
### (Optional: add OpenAI API key)
```bash
git clone https://github.com/nagyosse/trend-driven-category-system.git
cd trend-driven-category-system
cp .env.example .env

docker compose up --build

