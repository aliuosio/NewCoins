# PumpAndDump - Cryptocurrency Analysis Tool

A comprehensive cryptocurrency analysis tool that evaluates various technical and social indicators to provide investment recommendations.

## Features

- Analyzes cryptocurrencies using multiple technical indicators
- Evaluates social metrics including sentiment and developer activity
- Saves analysis results to a PostgreSQL database
- Provides historical data viewing and comparison
- Supports multiple cryptocurrencies in a single analysis
- Caches API responses for improved performance
- Tracks newly listed cryptocurrencies from MEXC exchange
- Monitors upcoming coin listings for investment opportunities
- Filters coins by listing timeframe

## Project Modules

### Analyse Module
The core analysis engine that evaluates cryptocurrencies using both technical and social indicators:
- **Technical Indicators**: Trading volume, liquidity, whale transactions, token distribution, pre-sale vesting, and smart contract audits
- **Social Indicators**: Sentiment analysis, developer activity, community growth, and Google Trends data
- Produces a comprehensive score and investment recommendation

### NewCoins Module

A tool for tracking new cryptocurrency listings:

- **API Integration**: Connects to MEXC exchange API for coin listings data
- **Time Filtering**: Configurable to track coins in specific time periods (24h, 48h, 72h)
- **Historical Data**: Retrieves coins listed in the past (last 24h, 48h)
- **Database Storage**: Saves coin data to PostgreSQL for analysis
- **Metadata**: Stores coin details including name, symbol, and listing times
- **Command-line Interface**: Parameter-based filtering for workflow integration

Useful for traders interested in newly listed tokens, which often have higher volatility during initial trading periods.

### Database Structure
- Uses PostgreSQL for persistent storage
- Maintains unique records for each cryptocurrency
- Updates existing records when new analyses are performed
- Supports historical data tracking and comparison

## Usage

### Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Configure your environment variables in `.env` file
4. Build and start the containers:

   docker-compose up -d

### Using the Analyzer Tool

# Basic usage - analyze Bitcoin (includes both technical and social indicators)
   
      python main.py analyze BTC

# Analyze multiple cryptocurrencies

      python main.py analyze BTC,ETH,SOL,DOGE

#### Analyze with verbose output

```bash
python main.py analyze BTC --verbose
```

### Using the NewCoins Tool

The NewCoins module fetches information about newly listed cryptocurrencies from the MEXC exchange API. This helps you discover and analyze new coins as soon as they're listed.

#### Fetch coins scheduled to be listed in the next 24 hours (default)

```bash
python src/NewCoins/main.py
```

#### Fetch coins scheduled to be listed in the next X hours

```bash
python src/NewCoins/main.py 48  # For next 48 hours
```

#### Fetch coins that were listed in the past X hours

```bash
python src/NewCoins/main.py -24  # For past 24 hours
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
