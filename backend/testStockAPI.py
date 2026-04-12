import yfinance as yf
import requests
import pandas as pd
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
            return render_template("sign_up.html", error="Email already taken!")

        # Insert new user
        result = supabase.table("users").insert({
            "email": email,
            "password": password
        }).execute()

        print(f"Insert result: {result.data}")  # Debug

        return redirect(url_for("login"))

    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query Supabase directly
        result = (
            supabase.table("users")
            .select("*")
            .eq("email", email)
            .eq("password", password)
            .execute()
        )

        if result.data:
            session['username'] = email
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    name = session.get('username')

    # Build stock table with buttons
    html_table = bs.BeautifulSoup(df.to_html(classes='data'), 'html.parser')
    rows = html_table.find_all('tr')
    first = True
    for row in rows:
        if first:
            tag = html_table.new_tag("td")
            tag.string = "Buttons"
            row.append(tag)
            first = False
        else:
            first_tag = html_table.new_tag("button", type="button")
            first_tag.string = "PRESS ME!"
            tag = html_table.new_tag('td')
            tag.append(first_tag)
            row.append(tag)

    # Get user's chosen stocks
    response = (supabase.table("chosen")
        .select("*")
        .execute()
    )
    user_options = pd.DataFrame(response.data)
    actual_user = user_options.loc[user_options['email'] == name]

    if request.method == "POST":
        stock = request.form.get("stock")
        condition = (df['name'] == stock)
        sCondition = (actual_user['ticker'] == stock)
        if df[condition].any(axis=None) and not(actual_user[sCondition].any(axis=None)):
            response = (
                supabase.table("chosen")
                .upsert({"email": name, "ticker": stock}, ignore_duplicates=True)
                .execute()
            )

    return render_template("dashboard.html", username=name, tables=[html_table], titles=df.columns.values)

@app.route("/userStocks")
def userStocks():
    name = session.get('username')
    response = (supabase.table("chosen")
        .select("*")
        .execute()
    )
    user_options = pd.DataFrame(response.data)
    actual_user = user_options.loc[user_options['email'] == name]

    return render_template("userStocks.html", username=name, tables=[actual_user.to_html()], titles=user_options.columns.values)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)