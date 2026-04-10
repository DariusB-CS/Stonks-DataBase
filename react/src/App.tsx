import StockTicker from "./components/StockTicker";
import Banner from "./components/Banner";
import Login from "./components/Login";
import "./App.css"

function App() {
	return (
	<div>
		<StockTicker />
      	<Banner />
		<div className = "container text-center"> 
			<div className = "row">
				<div className="col myCol">
					<h2>Stock Images
					</h2>
        		</div>
        		<div className="col myCol">
					<h2>Login:</h2>
					<img src="./src/assets/stock_bear.gif" 
					className="img-fluid" 
					style={{width: "50%", height: "auto"}}
					/>
					<Login />
        		</div>
      		</div>
		</div>
	</div>
	);
}

export default App;
