import Head from 'next/head';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#181B20] text-gray-100 flex flex-col items-center justify-center">
      <Head>
        <title>Crypto Indicator Report</title>
      </Head>
      <main className="w-full max-w-2xl p-8 rounded-xl shadow-lg bg-[#23272F] mt-12">
        <h1 className="text-3xl font-bold mb-2 text-white text-center">CRYPTO INDICATOR REPORT</h1>
        <p className="text-center text-gray-400 mb-8">[Token Name]</p>
        <div className="flex flex-col md:flex-row gap-8">
          <div className="flex-1 flex flex-col items-center">
            <div className="relative w-32 h-32 mb-4">
              {/* Placeholder for circular progress */}
              <svg width="128" height="128" viewBox="0 0 128 128">
                <circle cx="64" cy="64" r="56" stroke="#2C313A" strokeWidth="16" fill="none" />
                <circle cx="64" cy="64" r="56" stroke="#4F8EF7" strokeWidth="16" fill="none" strokeDasharray={2 * Math.PI * 56} strokeDashoffset={(1-0.76) * 2 * Math.PI * 56} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">76%</span>
                <span className="text-lg text-blue-400 font-bold">BUY</span>
              </div>
            </div>
            <div className="w-full">
              <h2 className="text-md font-bold text-gray-300 mb-2">SOCIAL INDICATORS</h2>
              <div className="space-y-2">
                <IndicatorBar label="Social Volume" score={8} />
                <IndicatorBar label="Sentiment Analysis" score={6} />
                <IndicatorBar label="Developer Activity" score={7} />
              </div>
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-md font-bold text-gray-300 mb-2">TECHNICAL INDICATORS</h2>
            <div className="space-y-2">
              <IndicatorBar label="Trading Volume" score={10} />
              <IndicatorBar label="Liquidity" score={8} />
              <IndicatorBar label="Whale Transactions" score={6} />
              <IndicatorBar label="Token Distribution" score={8} />
              <IndicatorBar label="Pre-Sale Vesting" score={5} />
              <IndicatorBar label="Smart Contract Audit" score={10} />
            </div>
          </div>
        </div>
        <div className="mt-8 grid md:grid-cols-2 gap-4">
          <div className="bg-[#22262C] border-l-4 border-blue-500 p-4 rounded">
            <h3 className="text-blue-400 font-bold mb-1">BUY</h3>
            <p className="text-gray-200 text-sm">The asset shows strong fundamentals with active development and decent liquidity. Keep an eye on token unlocks.</p>
          </div>
          <div className="bg-[#22262C] border-l-4 border-blue-500 p-4 rounded">
            <h3 className="text-blue-400 font-bold mb-1">INSIGHTS & HIGHLIGHTS</h3>
            <ul className="list-disc pl-5 text-gray-200 text-sm">
              <li>Strong liquidity with minimal slippage</li>
              <li>Upcoming token unlock: 12% of supply in 3 days</li>
              <li>High developer activity: 1110+ GitHub commits last 30d</li>
              <li>Moderate whale accumulation observed last 72h</li>
              <li>Positive sentiment at 78% – just below top score threshold</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

function IndicatorBar({ label, score }: { label: string; score: number }) {
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="text-gray-400">{score}/10</span>
      </div>
      <div className="w-full h-2 bg-[#23272F] rounded-full">
        <div
          className="h-2 rounded-full bg-blue-500"
          style={{ width: `${score * 10}%` }}
        />
      </div>
    </div>
  );
}
