import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], weight: ['400', '600', '700'] });

export default function Home() {
  return (
    <>
      <div style={{ color: 'red', fontSize: 30, fontWeight: 'bold', textAlign: 'center', marginBottom: 20 }}>
        HOT RELOAD TEST
      </div>
      <div className="min-h-screen flex items-center justify-center bg-bgDark text-primary font-sans">
        <div className="bg-bgCard rounded-[16px] p-8 w-[380px] max-w-[90%] shadow-lg flex flex-col gap-6">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div className="bg-[#242424] text-primary px-4 py-2 rounded-[10px] font-bold text-[1.1rem]">TOKEN NAME</div>
            <div className="font-semibold text-[0.95rem] text-primary cursor-pointer transition-colors duration-200 hover:text-[#FFA64D]">Overview &rarr;</div>
          </div>

          {/* Technical Indicators */}
          <div>
            <div className="font-bold text-[1rem] uppercase mt-4">Technical Indicators</div>
            <div className="flex flex-col gap-[0.6rem] mt-2">
              <div className="flex justify-between items-center text-[0.9rem]">
                <span className="flex items-center flex-1"><span className="mr-2">📈</span>Trading Volume</span>
                <div className="w-1/2 h-2 bg-[#2D2D2D] rounded ml-4">
                  <div className="h-full bg-primary rounded transition-all" style={{ width: '90%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-[0.9rem]">
                <span className="flex items-center flex-1"><span className="mr-2">💼</span>Liquidity</span>
                <div className="w-1/2 h-2 bg-[#2D2D2D] rounded ml-4">
                  <div className="h-full bg-primary rounded transition-all" style={{ width: '85%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Social Indicators */}
          <div>
            <div className="font-bold text-[1rem] uppercase mt-4">Social Indicators</div>
            <div className="flex flex-col gap-[0.6rem] mt-2">
              <div className="flex justify-between items-center text-[0.9rem]">
                <span className="flex items-center flex-1"><span className="mr-2">👥</span>Social Volume</span>
                <div className="w-1/2 h-2 bg-[#2D2D2D] rounded ml-4">
                  <div className="h-full bg-primary rounded transition-all" style={{ width: '75%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="border-t border-[#2D2D2D] pt-4 flex flex-col items-start">
            <div className="text-2xl font-bold text-primary">82%</div>
            <div className="bg-accent text-bgDark font-bold text-[0.9rem] px-5 py-2 rounded-[10px] mt-2">STRONG BUY</div>
            <div className="text-accent2 text-[0.9rem] mt-2">High potential for growth</div>
          </div>
        </div>
      </div>
    </>
  );
}
