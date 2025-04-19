# PumpAndDump - Cryptocurrency Analysis Tool

A tool for automated cryptocurrency analysis using technical and social indicators, with recommendations and database storage.

## Setup
1. Clone the repo and configure `.env`
2. Build and start containers:
   ```bash
- Updates existing records when new analyses are performed
- Supports historical data tracking and comparison

## Usage

### Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Configure your environment variables in `.env` file
4. Build and start the containers:

   docker-compose up -d

use `docker compose python bash` # to run below commands
# Basic usage - analyze Bitcoin (includes both technical and social indicators)

      
   
      python main.py analyze BTC

# Analyze multiple cryptocurrencies

Analyze coins (single or multiple):
```bash
python main.py analyze BTC
python main.py analyze BTC,ETH,SOL
```

Verbose analysis:
```bash
python main.py analyze BTC --verbose
```

Run the Scheduler:
```bash
python -m Scheduler.main

Fetched coins are saved to the database for later analysis.

## Features & Indicators

### Technical Indicators (70 points)
- **Trading Volume**: 24h volume, full score for ≥ $1M
- **Liquidity**: Bid/ask spread and depth, full points for ≤ 0.5% spread
- **Whale Transactions**: Detects accumulation/distribution
- **Token Distribution**: Circulation, Gini coefficient, holder diversity
- **Pre-Sale Vesting**: Upcoming unlocks, penalizes imminent large unlocks
- **Smart Contract Audit**: Security, audits, vulnerabilities

### Social Indicators (30 points)
- **Social Volume**: Mentions/discussions, full score for >10,000 mentions/24h
- **Sentiment Analysis**: Positive vs negative, full score for >80% positive
- **Developer Activity**: GitHub commits/contributors, full for 100+/20+

## Recommendations
Based on total score percentage:
- **STRONG BUY** (≥80%): High potential for growth
- **BUY** (≥70%): Good potential for growth
- **HOLD** (≥60%): Moderate potential
- **WATCH** (≥50%): Some concerns
- **AVOID** (<50%): Significant concerns
