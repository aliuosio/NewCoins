# NewCoins

*A comprehensive cryptocurrency analysis tool that evaluates technical and social indicators to provide investment recommendations.*

> This README expands the project overview, features, tech stack, setup, and contribution guidelines. It’s written for developers and power users who want to run or extend **NewCoins**.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start (Docker)](#quick-start-docker)
  - [CLI Usage](#cli-usage)
  - [Environment Variables](#environment-variables)
  - [Shutting Down](#shutting-down)
- [Project Structure](#project-structure)
- [Development Notes](#development-notes)
- [Contribution Guidelines](#contribution-guidelines)
- [Roadmap](#roadmap)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## Overview

**NewCoins** analyzes cryptocurrencies using a blend of **market/technical signals** and **social indicators** to generate a composite score and a clear recommendation (e.g., *BUY*, *HOLD*, *WATCH*, *AVOID*). It’s designed to help you quickly triage new or trending tokens and decide whether a deeper dive is warranted.

Primary audiences:
- Crypto traders who want a data-driven sanity check.
- Analysts and researchers exploring relationships between price/volume dynamics and social sentiment.
- Builders who want a Dockerized, extensible baseline for coin scoring and discovery.

---

## Features

### Technical indicators (weight ~70%)
- Trading volume (24h)
- Liquidity signals (spread / order book depth)
- Whale transactions (accumulation/distribution patterns)
- Token distribution (circulating supply, holder diversity)
- Vesting / unlock schedules
- Smart-contract audit status

### Social indicators (weight ~30%)
- Social volume (mentions/discussions)
- Sentiment tilt (positive vs. negative)
- Developer activity (e.g., commits / contributor counts)

### Scoring & recommendations
- A composite score (0–100) and a human-friendly label.
- Default thresholds:
  - **BUY** ≥ 50%
  - **HOLD** ≥ 40%
  - **WATCH** ≥ 30%
  - **AVOID** < 30%

### Discovery of upcoming listings
- Fetches **upcoming token listings** from MEXC within a time window (e.g., next 24h) and persists them to the database.

### Persistence & automation
- Stores results in **PostgreSQL** for historical analysis.
- Includes a **scheduler** (and `cron.sh`) to automate recurring jobs.

### Web dashboard (front-end)
- A `webapp/` folder is included for a browser UI to review results and recommendations.

---

## Architecture & Tech Stack

- **Backend:** Python 3 (analysis, data ingestion, scoring)
- **Database:** PostgreSQL (with some PL/pgSQL helpers)
- **Front-end:** TypeScript + HTML/CSS (in `webapp/`)
- **Containerization:** Docker & Docker Compose
- **Scripting/Automation:** Bash (`cron.sh`)

> Repo language composition (approx.): Python ~91%, TypeScript ~6%, PL/pgSQL ~1%, with small amounts of CSS/JS/Dockerfile.

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** installed
- (Optional) A text editor to configure environment variables

### Quick Start (Docker)

Clone the repo:
```bash
git clone https://github.com/aliuosio/NewCoins.git
cd NewCoins
```

Copy the example environment file and edit it:
```bash
cp .env.example .env
# open .env and adjust values (DB credentials, API URLs/keys, etc.)
```

Bring the stack up:
```bash
docker compose up -d
```

Enter the Python container when you want to run CLI commands interactively:
```bash
docker compose exec python bash
```

### CLI Usage

Analyze single or multiple coins:
```bash
python main.py analyze BTC
python main.py analyze BTC,ETH,SOL
```

Verbose output:
```bash
python main.py analyze BTC --verbose
```

Run the scheduler:
```bash
python Scheduler/main.py
```

Fetch *upcoming* coins from **MEXC** (persists to DB):
```bash
# default window: next 24 hours
python -m NewCoins.main

# set a custom window in hours:
python -m NewCoins.main 48    # next 48 hours
python -m NewCoins.main -12   # past 12 hours
```

### Environment Variables

Create and maintain a `.env` in the project root. See `.env.example` for the authoritative list. Typical keys include:

- **Database**
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_HOST`
  - `POSTGRES_PORT`
- **External / API**
  - `MEXC_HTTP_URL` (required for the MEXC listings fetcher)
  - Any additional API keys/URLs you choose to integrate

> Keep secrets out of source control. Use `.env` and, for production, consider Docker secrets or a secret manager.

### Shutting Down

```bash
docker compose down
```

(Add `-v` to remove volumes if you want a clean slate, but you’ll lose any stored data.)

---

## Project Structure

```
NewCoins/
├─ .docker/             # Docker helpers, entrypoints, etc.
├─ cache/               # (Optional) local caches, temp artifacts
├─ src/                 # Python backend (analysis, ingestion, scoring)
├─ webapp/              # Front-end dashboard
├─ .env.example         # Copy to .env and configure
├─ cron.sh              # Example cron entrypoint / scheduling helper
├─ docker-compose.yml   # Multi-service orchestration
└─ README.md            # You are here
```

---

## Development Notes

- Prefer **PEP 8** for Python; type hints encouraged where sensible.
- Use small, testable functions and clear module boundaries.
- Keep external API calls wrapped so they can be mocked in tests later.
- Avoid committing credentials; `.env` is for local dev only.
- If you add new indicators, document:
  - inputs (data needed),
  - method (formula / heuristic),
  - weight (impact on total score).

---

## Contribution Guidelines

We welcome contributions of all sizes.

1. **Fork** the repo and **create a feature branch**:
   ```bash
   git checkout -b feature/your-idea
   ```
2. **Commit small, cohesive changes** with clear messages.
3. **Open a Pull Request** describing the “why” and “what”; link related issues.
4. Be responsive to **code review**—we keep the bar high but friendly.
5. For larger changes, consider opening an **issue** first to discuss direction.

**Coding style**: PEP 8 (Python), consistent TypeScript/HTML/CSS for the UI. Favor clarity, tests where it makes sense, and up-to-date docs.

---

## Roadmap

- More exchange integrations for discovery
- Pluggable data sources for sentiment/on-chain metrics
- Richer dashboard: filtering, historical trends, alerting
- Configurable weights/thresholds per indicator profile
- CI for linting/tests
---

## Disclaimer

This project is for **research and educational purposes only** and does **not** constitute financial advice. Crypto assets are volatile—do your own research and manage risk appropriately.
