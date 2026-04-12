function Banner() {
  return (
    <div style={{ position: "relative", backgroundColor: "#111", height: "100vh", overflow: "hidden" }}>
      <style>{`
        .lines {
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 100%;
          margin: auto;
          width: 90vw;
          display: flex;
          justify-content: space-between;
        }
        .line {
          position: relative;
          width: 40px;
          height: 100%;
          overflow: hidden;
          text-align: center;
        }
        .line::after {
          content: '$';
          font-size: 1.2rem;
          display: block;
          position: absolute;
          height: 15vh;
          width: 100%;
          top: -50%;
          left: 0;
          animation: drop 7s 0s infinite;
          animation-fill-mode: forwards;
          animation-timing-function: cubic-bezier(0.4, 0.26, 0, 0.97);
        }
        .line:nth-child(1)::after  { color: #FF4500; animation-delay: 0.5s; }
        .line:nth-child(2)::after  { color: #32CD32; animation-delay: 1s; }
        .line:nth-child(3)::after  { color: #1E90FF; animation-delay: 1.5s; }
        .line:nth-child(4)::after  { color: #FFD700; animation-delay: 2s; }
        .line:nth-child(5)::after  { color: #8A2BE2; animation-delay: 2.5s; }
        .line:nth-child(6)::after  { color: #20B2AA; animation-delay: 3s; }
        .line:nth-child(7)::after  { color: #DC143C; animation-delay: 3.5s; }
        .line:nth-child(8)::after  { color: #00FA9A; animation-delay: 4s; }
        .line:nth-child(9)::after  { color: #FF1493; animation-delay: 4.5s; }
        .line:nth-child(10)::after { color: #00BFFF; animation-delay: 5s; }
        @keyframes drop {
          0%   { top: -50%; }
          100% { top: 110%; }
        }
      `}</style>

      {/* Animated background lines */}
      <div className="lines">
        {[...Array(10)].map((_, i) => (
          <div className="line" key={i}></div>
        ))}
      </div>

      {/* Hero text on top */}
      <div style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        textAlign: "center",
        zIndex: 1,
      }}>
        <h1 style={{ fontSize: "80px", color: "#3c7a18" }}>Social Stonks</h1>
        <h2 style={{ fontSize: "30px", color: "#ffffff" }}>Bringing Wall Street to you.</h2>
      </div>
    </div>
  );
}

export default Banner;
