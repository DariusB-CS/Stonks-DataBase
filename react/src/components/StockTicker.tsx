
// Types
interface StockItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

// Mock Data
const stocks : StockItem[] = [
  { symbol: "AAPL", price: 189.50, change: 2.30, changePercent: 1.23 },
  { symbol: "TSLA", price: 245.10, change: -5.40, changePercent: -2.16},
  { symbol: "MSFT", price: 415.80, change: -8.98, changePercent: -2.24},
  { symbol: "NVDA", price: 177.19, change: -7.70, changePercent: -4.16},
  { symbol: "NFLX", price: 96.24, change: 11.65, changePercent: 13.77},
  { symbol: "SOFI", price: 17.76, change: -1.34, changePercent: -7.02},
  { symbol: "NU", price: 14.98, change: -0.08, changePercent: -0.53},
  { symbol: "MARA", price: 8.94, change: 0.49, changePercent: 5.80},
  { symbol: "PSKY", price: 13.51, change: 2.33, changePercent: 20.84},
];

// Single Stock Entry
const StockEntry : React.FC<{ stock: StockItem }> = ({stock}) => {
  const isPositive = stock.change >= 0;
  const color = isPositive ? "#00ff9f" : "#ff4d6d";
  const arrow = isPositive ? "▲" : "▼";

  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "0.6rem", padding: "0 2.5rem" }}>
    
    <span style={{
      fontFamily: "'Bebas Neue', 'Impact', sans-sherif",
      fontSize: "1.05rem",
      letterSpacing: "0.12em",
      color: "#ffffff",
    }}>
      {stock.symbol}
    </span>

    <span style={{
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: "0.95rem",
      color: "#e2e8f0",
    }}>
      ${stock.price.toFixed(2)}
    </span>
 
    {/* Change */}
      <span style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: "0.85rem",
        color,
      }}>
        {arrow} {isPositive ? "+" : ""}{stock.change.toFixed(2)} ({isPositive ? "+" : ""}{stock.changePercent.toFixed(2)}%)
      </span>

      {/* Divider dot */}
      <span style={{ color: "#334155", fontSize: "1.2rem", lineHeight: 1 }}>◆</span>
    </span>
  );
};

// --- Ticker Banner ---
const StockTicker: React.FC = () => {
  // Duplicate the list so the loop is seamless
  const allStocks = [...stocks, ...stocks];

  return (
    <>
      {/* Inject keyframe animation + Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&display=swap');

        @keyframes ticker-scroll {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }

        .ticker-track {
          display: inline-flex;
          white-space: nowrap;
          animation: ticker-scroll 35s linear infinite;
        }

        .ticker-track:hover {
          animation-play-state: paused;
        }

        .ticker-fade-left {
          background: linear-gradient(to right, #020817 0%, transparent 8%);
        }

        .ticker-fade-right {
          background: linear-gradient(to left, #020817 0%, transparent 8%);
        }
      `}</style>

      {/* Outer banner */}
      <div style={{
        width: "100%",
        background: "linear-gradient(90deg, #020817 0%, #0d1b2a 50%, #020817 100%)",
        borderBottom: "1px solid #1e3a5f",
        borderTop: "1px solid #1e3a5f",
        padding: "0.6rem 0",
        overflow: "hidden",
        position: "relative",
        boxShadow: "0 0 30px rgba(0, 200, 255, 0.07)",
      }}>

        {/* Fade overlays on edges */}
        <div className="ticker-fade-left" style={{
          position: "absolute", left: 0, top: 0, bottom: 0, width: "6rem", zIndex: 2, pointerEvents: "none",
        }} />
        <div className="ticker-fade-right" style={{
          position: "absolute", right: 0, top: 0, bottom: 0, width: "6rem", zIndex: 2, pointerEvents: "none",
        }} />

        {/* Scrolling track */}
        <div className="ticker-track">
          {allStocks.map((stock, i) => (
            <StockEntry key={`${stock.symbol}-${i}`} stock={stock} />
          ))}
        </div>
      </div>
    </>
  );
};

export default StockTicker;
