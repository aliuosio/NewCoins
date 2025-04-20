# PumpAndDump - Cryptocurrency Analysis Tool

A tool for automated cryptocurrency analysis using technical and social indicators, with recommendations and database storage.

## Setup

1. Make sure you have Docker and Docker Compose installed.
2. Clone this repository and configure your environment variables in the `.env` file.
3. Build and start the containers:
   ```bash
   docker compose up -d
   ```
4. Enter the Python container shell to run commands:
   ```bash
   docker compose exec python bash
   ```

## Usage

### Analyze coins (single or multiple):

```bash
python main.py analyze BTC
python main.py analyze BTC,ETH,SOL
```

### Verbose analysis:

```bash
python main.py analyze BTC --verbose
```

### Run the Scheduler:

```bash
python -m Scheduler.main
```

### Fetch and persist new coins (MEXC):

Fetch new coins scheduled to launch on MEXC within a specified time window (default: next 24 hours). Results are saved to the database.

```bash
python -m NewCoins.main [hours]
```
- `[hours]` (optional): Positive for next hours, negative for past hours (default: 24)
- Requires the `MEXC_HTTP_URL` environment variable set in your `.env` file

**Example:**
```bash
 24    # Next 24 hours
python -m NewCoins.main -12   # Past 12 hours
```

The script will output the number of coins found and persist them to the database.

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
- **BUY** (≥50%): Good potential for growth
- **HOLD** (≥40%): Moderate potential
- **WATCH** (≥30%): Some concerns
- **AVOID** (≥20%): Significant concerns
python -m NewCoins.main