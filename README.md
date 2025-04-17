# PumpAndDump - Cryptocurrency Analysis Tool

A comprehensive cryptocurrency analysis tool that evaluates various technical and social indicators to provide investment recommendations.

## Features

- Analyzes cryptocurrencies using multiple technical indicators
- Evaluates social metrics including sentiment and developer activity
- Saves analysis results to a PostgreSQL database
- Provides historical data viewing and comparison
- Supports multiple cryptocurrencies in a single analysis
- Caches API responses for improved performance

## Usage

### Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Configure your environment variables in `.env` file
4. Build and start the containers:

```bash
docker-compose up -d
```

### Using the Analyzer Tool

The `analyzer.py` script provides two main commands: `analyze` and `report`.

#### Analyzing Cryptocurrencies

```bash
# Basic usage - analyze Bitcoin (includes both technical and social indicators)
python analyzer.py analyze BTC

# Analyze multiple cryptocurrencies
python analyzer.py analyze BTC,ETH,SOL,DOGE

# Show detailed analysis information
python analyzer.py analyze BTC --verbose

# Save results to database
python analyzer.py analyze BTC --save
```

#### Viewing Saved Analysis Results

```bash
# View all analyses (both technical and social)
python analyzer.py report

# View only technical indicators
python analyzer.py report --type technical

# View only social indicators
python analyzer.py report --type social

# Filter by specific cryptocurrency
python analyzer.py report --symbol BTC

# Limit to analyses from the last N days
python analyzer.py report --days 7

# Limit number of results
python analyzer.py report --limit 5

# Combine filters
python analyzer.py report --symbol ETH --days 30 --limit 10 --type social
```

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
