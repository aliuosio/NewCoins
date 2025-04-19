// Simple mock API endpoint for indicators
type Indicator = { name: string; value: number };

const technical: Record<string, Indicator[]> = {
  BTC: [
    { name: 'Trading Volume', value: 90 },
    { name: 'Liquidity', value: 85 },
    { name: 'Whale Transactions', value: 70 },
    { name: 'Token Distribution', value: 40 },
    { name: 'Pre-Sale Vesting', value: 50 },
    { name: 'Smart Contract Audit', value: 30 },
  ],
  ETH: [
    { name: 'Trading Volume', value: 80 },
    { name: 'Liquidity', value: 88 },
    { name: 'Whale Transactions', value: 60 },
    { name: 'Token Distribution', value: 55 },
    { name: 'Pre-Sale Vesting', value: 45 },
    { name: 'Smart Contract Audit', value: 40 },
  ],
  SOL: [
    { name: 'Trading Volume', value: 60 },
    { name: 'Liquidity', value: 70 },
    { name: 'Whale Transactions', value: 50 },
    { name: 'Token Distribution', value: 60 },
    { name: 'Pre-Sale Vesting', value: 35 },
    { name: 'Smart Contract Audit', value: 20 },
  ],
  DOGE: [
    { name: 'Trading Volume', value: 40 },
    { name: 'Liquidity', value: 60 },
    { name: 'Whale Transactions', value: 80 },
    { name: 'Token Distribution', value: 30 },
    { name: 'Pre-Sale Vesting', value: 20 },
    { name: 'Smart Contract Audit', value: 10 },
  ],
};

const social: Record<string, Indicator[]> = {
  BTC: [
    { name: 'Social Volume', value: 75 },
    { name: 'Sentiment Analysis', value: 65 },
    { name: 'Developer Activity', value: 45 },
  ],
  ETH: [
    { name: 'Social Volume', value: 70 },
    { name: 'Sentiment Analysis', value: 60 },
    { name: 'Developer Activity', value: 55 },
  ],
  SOL: [
    { name: 'Social Volume', value: 55 },
    { name: 'Sentiment Analysis', value: 50 },
    { name: 'Developer Activity', value: 60 },
  ],
  DOGE: [
    { name: 'Social Volume', value: 80 },
    { name: 'Sentiment Analysis', value: 40 },
    { name: 'Developer Activity', value: 30 },
  ],
};

export default function handler(req, res) {
  const token = (req.query.token || 'BTC').toUpperCase();
  res.status(200).json({
    technical: technical[token] || technical.BTC,
    social: social[token] || social.BTC,
  });
}
