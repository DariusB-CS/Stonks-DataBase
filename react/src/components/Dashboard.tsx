import { useState, useEffect } from "react";
import StockTicker from "./StockTicker";
import StockChart from "./StockChart";

interface Stock {
    name: string;
    price: number;
    change_in_price: number;
    volume: number;
    market_cap: number | null;
    p_to_e_ratio: number | null;
}

const mockStocks: Stock[] = [
    { name: "AAPL",  price: 260.48, change_in_price: 0.50,   volume: 31259500, market_cap: null, p_to_e_ratio: null },
    { name: "TSLA",  price: 245.10, change_in_price: -5.40,  volume: 8200000,  market_cap: null, p_to_e_ratio: null },
    { name: "MSFT",  price: 415.80, change_in_price: -8.98,  volume: 5100000,  market_cap: null, p_to_e_ratio: null },
    { name: "NVDA",  price: 177.19, change_in_price: -7.70,  volume: 9800000,  market_cap: null, p_to_e_ratio: null },
    { name: "NFLX",  price: 96.24,  change_in_price: 11.65,  volume: 4300000,  market_cap: null, p_to_e_ratio: null },
    { name: "SOFI",  price: 17.76,  change_in_price: -1.34,  volume: 2100000,  market_cap: null, p_to_e_ratio: null },
    { name: "MARA",  price: 8.94,   change_in_price: 0.49,   volume: 1500000,  market_cap: null, p_to_e_ratio: null },
    { name: "GOOGL", price: 175.32, change_in_price: 2.10,   volume: 7600000,  market_cap: null, p_to_e_ratio: null },
    { name: "AMZN",  price: 198.45, change_in_price: -3.20,  volume: 6400000,  market_cap: null, p_to_e_ratio: null },
    { name: "META",  price: 512.30, change_in_price: 8.75,   volume: 4900000,  market_cap: null, p_to_e_ratio: null },
    { name: "AMD",   price: 142.67, change_in_price: -4.33,  volume: 3800000,  market_cap: null, p_to_e_ratio: null },
    { name: "PYPL",  price: 68.90,  change_in_price: 1.20,   volume: 2200000,  market_cap: null, p_to_e_ratio: null },
    { name: "INTC",  price: 21.45,  change_in_price: -0.85,  volume: 5100000,  market_cap: null, p_to_e_ratio: null },
    { name: "NU",    price: 14.98,  change_in_price: -0.08,  volume: 1800000,  market_cap: null, p_to_e_ratio: null },
    { name: "PSKY",  price: 13.51,  change_in_price: 2.33,   volume: 900000,   market_cap: null, p_to_e_ratio: null },
];

function Dashboard() {
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [search, setSearch] = useState("");
    const [filtered, setFiltered] = useState<Stock[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedStock, setSelectedStock] = useState<string | null>(null);

    useEffect(() => {
        fetch("/api/stocks")
    .then((res) => res.json())
    .then((data) => {
        setStocks(data.stocks);
        setFiltered(data.stocks);
        setLoading(false);
    })
    .catch(() => {
        setError("Failed to load stocks.");
        setLoading(false);
    });
    }, []);

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        const query = e.target.value.toUpperCase();
        setSearch(query);
        setFiltered(stocks.filter((s) => s.name.toUpperCase().includes(query)));
        setSelectedStock(null);
    };

    const handleRowClick = (ticker: string) => {
        setSelectedStock(selectedStock === ticker ? null : ticker);
    };

    const handleLogout = async () => {
        await fetch("/logout");
        window.location.href = "/";
    };

    const totalGainers = stocks.filter((s) => s.change_in_price >= 0).length;
    const totalLosers  = stocks.filter((s) => s.change_in_price < 0).length;

    return (
        <div style={{ minHeight: "100vh", backgroundColor: "#3c7a18" }}>
            <StockTicker />

            {/* Navbar */}
            <nav className="navbar px-4 py-2 d-flex justify-content-between align-items-center"
                style={{ backgroundColor: "#2d5e12" }}>
                <span style={{ color: "#fff", fontSize: "1.5rem", fontWeight: "bold" }}>
                    📈 Social Stonks
                </span>
                <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
                    Logout
                </button>
            </nav>

            <div className="container py-4">

                {/* Summary Cards */}
                <div className="row mb-4 g-3">
                    <div className="col-md-4">
                        <div style={{
                            backgroundColor: "#2d5e12", borderRadius: "8px",
                            padding: "20px", color: "#fff", textAlign: "center",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
                        }}>
                            <h6 style={{ color: "#a8d5a2" }}>Total Stocks</h6>
                            <h2>{stocks.length}</h2>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div style={{
                            backgroundColor: "#2d5e12", borderRadius: "8px",
                            padding: "20px", color: "#00ff9f", textAlign: "center",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
                        }}>
                            <h6 style={{ color: "#a8d5a2" }}>Gainers</h6>
                            <h2>▲ {totalGainers}</h2>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div style={{
                            backgroundColor: "#2d5e12", borderRadius: "8px",
                            padding: "20px", color: "#ff4d6d", textAlign: "center",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
                        }}>
                            <h6 style={{ color: "#a8d5a2" }}>Losers</h6>
                            <h2>▼ {totalLosers}</h2>
                        </div>
                    </div>
                </div>

                {/* Search Bar */}
                <div className="row mb-3">
                    <div className="col-md-6 mx-auto">
                        <input
                            type="text"
                            className="form-control form-control-lg"
                            placeholder="🔍 Search stocks e.g. AAPL, TSLA..."
                            value={search}
                            onChange={handleSearch}
                            style={{
                                backgroundColor: "#fff",
                                border: "2px solid #2d5e12",
                                borderRadius: "8px",
                            }}
                        />
                    </div>
                </div>

                {/* Hint */}
                <div className="text-center mb-3">
                    <small style={{ color: "#d4edda" }}>
                        💡 Click any stock row to view its 30-day price chart
                    </small>
                </div>

                {/* Stock Table */}
                {loading ? (
                    <div className="text-center text-white">
                        <div className="spinner-border" role="status" />
                        <p className="mt-2">Loading stocks...</p>
                    </div>
                ) : error ? (
                    <div className="alert alert-danger">{error}</div>
                ) : (
                    <div className="row">
                        <div className="col">
                            <div style={{
                                backgroundColor: "#fff",
                                borderRadius: "8px",
                                overflow: "hidden",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
                            }}>
                                <table className="table table-hover mb-0">
                                    <thead style={{ backgroundColor: "#2d5e12", color: "#fff" }}>
                                        <tr>
                                            <th>Ticker</th>
                                            <th>Price</th>
                                            <th>Change</th>
                                            <th>Volume</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filtered.length > 0 ? (
                                            filtered.map((stock) => (
                                                <>
                                                    <tr
                                                        key={stock.name}
                                                        onClick={() => handleRowClick(stock.name)}
                                                        style={{
                                                            cursor: "pointer",
                                                            backgroundColor: selectedStock === stock.name ? "#f0f7ee" : "",
                                                            transition: "background-color 0.2s"
                                                        }}
                                                    >
                                                        <td>
                                                            <strong>{stock.name}</strong>
                                                            {selectedStock === stock.name && (
                                                                <span style={{ color: "#2d5e12", marginLeft: "8px", fontSize: "0.8rem" }}>
                                                                    ▼ chart
                                                                </span>
                                                            )}
                                                        </td>
                                                        <td>${stock.price.toFixed(2)}</td>
                                                        <td style={{
                                                            color: stock.change_in_price >= 0 ? "#2d5e12" : "#dc3545",
                                                            fontWeight: "bold"
                                                        }}>
                                                            {stock.change_in_price >= 0 ? "▲" : "▼"} {Math.abs(stock.change_in_price).toFixed(2)}
                                                        </td>
                                                        <td>{stock.volume.toLocaleString()}</td>
                                                    </tr>

                                                    {/* Expandable Chart Row */}
                                                    {selectedStock === stock.name && (
                                                        <tr key={`${stock.name}-chart`}>
                                                            <td colSpan={4} style={{ padding: "0 16px 16px 16px", backgroundColor: "#f9fafb" }}>
                                                                <StockChart
                                                                    ticker={stock.name}
                                                                    onClose={() => setSelectedStock(null)}
                                                                />
                                                            </td>
                                                        </tr>
                                                    )}
                                                </>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan={4} className="text-center text-muted py-4">
                                                    No stocks found for "<strong>{search}</strong>"
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Dashboard;