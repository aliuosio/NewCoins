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
```

This fetches, analyzes, and prints cronjob lines for coins with a "BUY" or "STRONG BUY" recommendation (default: last 24h).
   
      python main.py analyze BTC

# Analyze multiple cryptocurrencies

      python main.py analyze BTC,ETH,SOL,DOGE

#### Analyze with verbose output

```bash
python main.py analyze BTC --verbose
```

### Using the NewCoins Tool

The NewCoins module fetches information about newly listed cryptocurrencies from the MEXC exchange API. This helps you discover and analyze new coins as soon as they're listed.

### Using the Scheduler Tool

The Scheduler automates the process of:
1. Fetching new coins from MEXC (using the NewCoins module)
2. Analyzing those coins with the Analyzer
3. Checking the analysis summary view for coins with a strong recommendation
4. Printing (or creating) cronjobs for a fictive trading script for qualifying coins

#### Run the Scheduler (default: last 24h)

```bash
python src/Scheduler/main.py
```

- This will fetch and persist new coins, analyze them, and print out cronjob lines for coins with a "BUY" or "STRONG BUY" recommendation.
- By default, it considers coins added in the last 24 hours (adjustable in the code).

#### Fetch coins scheduled to be listed in the next 24 hours (default)

```bash
python NewCoins/main.py
```

#### Fetch coins scheduled to be listed in the next X hours

```bash
python NewCoins/main.py 48  # For next 48 hours
```

#### Fetch coins that were listed in the past X hours

```bash
python NewCoins/main.py -24  # For past 24 hours
```

The fetched coins are automatically saved to the database for later analysis.

## Indicators

### Technical Indicators (70 points total)

1. **Trading Volume** (15 points)
   - Measures 24h trading volume with full score for volume ≥ $1M

2. **Liquidity** (15 points)
   - Evaluates bid/ask spread and market depth
   - Targets spread of 0.5% or less for full points

3. **Whale Transactions** (10 points)
   - Analyzes volume spikes and price patterns
   - Detects accumulation/distribution patterns

4. **Token Distribution** (10 points)
   - Evaluates circulation ratio, Gini coefficient, holder diversity
   - Rewards more equal distribution and active communities

5. **Pre-Sale Vesting** (10 points)
   - Analyzes upcoming token unlocks and their market impact
   - Lower score for imminent large unlocks

6. **Smart Contract Audit** (10 points)
   - Assesses contract security, audits, and vulnerabilities
   - Higher score for multiple audits by reputable firms

### Social Indicators (30 points total)

1. **Social Volume** (10 points)
   - Measures mentions and discussions across social platforms
   - Full score for high discussion volume (>10,000 mentions in 24h)

2. **Sentiment Analysis** (10 points)
   - Evaluates positive vs negative sentiment across platforms
   - Higher score for predominantly positive sentiment (>80% positive)

3. **Developer Activity** (10 points)
   - Tracks GitHub commits and contributors
   - Higher score for active development (100+ commits, 20+ contributors)

## Recommendations

Based on the total score percentage, the tool provides one of these recommendations:

- **STRONG BUY** (≥80%): High potential for growth
- **BUY** (≥70%): Good potential for growth
- **HOLD** (≥60%): Moderate potential
- **WATCH** (≥50%): Some concerns
- **AVOID** (<50%): Significant concerns
