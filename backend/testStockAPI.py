import yfinance as yf
import requests
import pandas as pd
import uuid
from sqlalchemy import create_engine
import bs4 as bs
from flask import Flask, request, render_template, url_for, redirect, session
import bcrypt
from supabase import create_client, Client
import os 
from dotenv import load_dotenv, dotenv_values
load_dotenv()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15 Ddg/18.6'}
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers)
soup = bs.BeautifulSoup(resp.text, 'lxml')
table = soup.find('table')

tickers = []
for row in table.find_all('tr')[1:]:
    ticker = row.find_all('td')[0].text
    tickers.append(ticker)
tickers = [s.replace('\n', '') for s in tickers]

data = yf.download(tickers, period='1d', auto_adjust=False)
print(data.head())
df = data.stack().reset_index().rename(index=str, columns={"level_1": "Ticker"}).sort_values(['Ticker'])
df = df.drop("Date", axis=1)
df = df.dropna()
print(df.head())

# ── Rename columns to match Supabase schema ──────────────────────────────────
df = df.rename(columns={
    "Ticker":    "name",
    "Close":     "price",
    "Open":      "open",
    "Volume":    "volume",
})

# Calculate change_in_price from Close - Open
df["change_in_price"] = df["price"] - df["open"]

# Placeholders for columns yfinance doesn't provide in daily data
df["market_cap"]  = None
df["p_to_e_ratio"] = None

# Keep only columns Supabase expects (drop open since it's not in schema)
df = df[["name", "price", "change_in_price", "market_cap", "volume", "p_to_e_ratio"]]
print(df.head())
# ─────────────────────────────────────────────────────────────────────────────

# Round numeric columns to match Supabase types
df["price"] = df["price"].round(2)
df["change_in_price"] = df["change_in_price"].round(2)
df["volume"] = df["volume"].astype(int) # bigint needs whole numbers

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Get users from Supabase
response = (supabase.table("users")
        .select("*")
        .execute()
)
table_df = pd.DataFrame(response.data)

# Round numeric columns to match Supabase types
df["price"] = df["price"].round(2)
df["change_in_price"] = df["change_in_price"].round(2)
df["volume"] = df["volume"].astype(int)

# Upload stock data to Supabase
response = (
    supabase.table("stocks")
    .upsert(df.to_dict('records'))
    .execute()
)
print("Stocks uploaded successfully!")

# ── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'nananabobo'


@app.route("/")
def home():
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            email = data.get("username") or data.get("email")
            password = data.get("password")
        else:
            email = request.form.get("username") or request.form.get("email")
            password = request.form.get("password")

        print(f"Attempting to register: {email}")  # Debug

        if not email or not password:
            return {"error": "Email and password required"}, 400

        # Query Supabase directly instead of using stale table_df
        existing = (
            supabase.table("users")
            .select("*")
            .eq("email", email)
            .execute()
        )

        print(f"Existing query result: {existing.data}")  # Debug

        if existing.data:  # Username already exists
            return {"error": "Email already taken!"}, 409

        # Insert new user
        result = supabase.table("users").insert({
            "id": str(uuid.uuid4()),
            "email": email,
            "password": password
        }).execute()

        print(f"Insert result: {result.data}")  # Debug

        return {"success": True}, 200

    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            email = data.get("username") or data.get("email")
            password = data.get("password")
        else:
            email = request.form.get("username") or request.form.get("email")
            password = request.form.get("password")

        print(f"Attempting to login: {email}")

        result = (
            supabase.table("users")
            .select("*")
            .eq("email", email)
            .eq("password", password)
            .execute()
        )

        print(f"Login result: {result.data}")

        if result.data:
            session['username'] = email
            return {"success": True}, 200
        else:
            return {"error": "Invalid email or password"}, 401

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    name = session.get('username')
    if not name:
        return redirect(url_for("login"))

    if request.method == "POST":
        stock_name = request.form.get("stock")
        if stock_name:
            # 1. Fetch User ID from the 'users' table using the session email
            user_res = supabase.table("users").select("id").eq("email", name).execute()
            # 2. Fetch Stock ID and current price from the 'stocks' table
            stock_res = supabase.table("stocks").select("id", "price").eq("name", stock_name).execute()
            
            if user_res.data and stock_res.data:
                user_id = user_res.data[0]["id"]
                stock_id = stock_res.data[0]["id"]
                current_price = stock_res.data[0]["price"]

                # 3. Insert into 'tracked_stocks' referencing the specific IDs
                supabase.table("tracked_stocks").insert({
                    "user_id": user_id,
                    "stock_id": stock_id,
                    "Price": current_price,
                }).execute()

        return redirect(url_for("dashboard"))

    # Build stock table with buttons
    html_table = bs.BeautifulSoup(df.to_html(classes='data', index=False), 'html.parser')
    rows = html_table.find_all('tr')

    for i, row in enumerate(rows):
        if i == 0:
            # Header row
            action_header = html_table.new_tag("th")
            action_header.string = "Actions"
            row.append(action_header)
            continue

        # Skip rows that don't map to df rows
        if i - 1 >= len(df):
            continue

        stock_name = df.iloc[i - 1]["name"]

    # Create <form method="POST">
    form_tag = html_table.new_tag("form", attrs={"method": "POST"})

    # Hidden input
    input_tag = html_table.new_tag(
        "input",
        attrs={
            "type": "hidden",
            "name": "stock",
            "value": stock_name
        }
    )

    # Submit button
    button_tag = html_table.new_tag(
        "button",
        attrs={"type": "submit"}
    )
    button_tag.string = "Track Stock"

    # Assemble form
    form_tag.append(input_tag)
    form_tag.append(button_tag)

    # Add form into a new table cell
    action_cell = html_table.new_tag("td")
    action_cell.append(form_tag)
    row.append(action_cell)


    return render_template("dashboard.html", username=name, tables=[html_table], titles=df.columns.values)

@app.route("/userStocks")
def userStocks():
    name = session.get('username')
    if not name:
        return redirect(url_for("login"))

    # Fetch the user's ID
    user_res = supabase.table("users").select("id").eq("email", name).execute()
    if not user_res.data:
        return redirect(url_for("logout"))
    
    user_id = user_res.data[0]["id"]

    # Fetch tracked stocks joined with details from the 'stocks' table
    response = (supabase.table("tracked_stocks")
        .select("Price, created_at, stocks(name, volume, market_cap)")
        .eq("user_id", user_id)
        .execute()
    )
    
    # Flatten the joined data into a readable DataFrame
    tracked_df = pd.json_normalize(response.data)
    if not tracked_df.empty:
        tracked_df.columns = [c.replace('stocks.', '') for c in tracked_df.columns]

    return render_template("userStocks.html", username=name, tables=[tracked_df.to_html(classes='data', index=False)], titles=tracked_df.columns.values)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)