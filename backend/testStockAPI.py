import yfinance as yf
import requests
import pandas as pd
#import mysql.connector
from sqlalchemy import create_engine # make sure to also pip install pymysql
import bs4 as bs
from flask import Flask, request, render_template, url_for, redirect, session
import bcrypt
from supabase import create_client, Client
import os 
from dotenv import load_dotenv, dotenv_values
load_dotenv()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15 Ddg/18.6'} # Make sure you change the user agent to fit your browser
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies' , headers=headers) # Get the website information from wikipedia
soup = bs.BeautifulSoup(resp.text, 'lxml') # Parse it using beautiful soup to get the html information
table = soup.find('table') # Find the table that has the S&P 500 tickers

tickers = []

for row in table.find_all('tr')[1:]: # tr is the table row and you skip that first row
    ticker = row.find_all('td')[0].text # td [0] gives you the first column which is the ticker name
    tickers.append(ticker) 
tickers = [s.replace('\n', '') for s in tickers] # Remove the newline character from each ticker name

data = yf.download(tickers, period ='1d', auto_adjust = False) # Get the full ticker information from yfinance
print(data.head())
df = data.stack().reset_index().rename(index=str, columns={"level_1": "Ticker"}).sort_values(['Ticker']) # Trying to make it look better and more organized
df = df.drop("Date", axis = 1) # Dropping the date because it isn't needed and might give an error
df = df.dropna()
print(df.head()) # Gets the tail end of all the data

url: str = os.environ.get("SUPABASE_URL") #gets the username and key from the .env file
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key) #connects to supabase

response = (supabase.table("USERS") # Gets the user information from the supabase table
        .select("*")
        .execute()
)

table_df = pd.DataFrame(response.data) # Makes the users into a pandas table for easy changing



response = ( # Puts all the stock information into the supabase table
            supabase.table("STOCKS")
            .upsert(df.to_dict('records'))
            .execute()
        )



app = Flask(__name__) # Initiating the flask
app.secret_key = 'nananabobo' # need a key to be able to use the session dict

#@app.route("/stocks") # Making the route from the main website
#def stocks(): # Calling the website function
 # return df.to_html() # Making the pandas dataframe into an html thingy
#  return df.to_json() # to html looks prettier

@app.route('/register', methods=["GET", "POST"]) # the post lets it get info from website
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") # hash the password
        condition = (table_df['UserN'] == username)
# The line above gets the username
        if table_df[condition].any(axis=None): # Should probably check just the username
            return render_template("sign_up.html", error="Username already taken!")

        table_df.loc[len(table_df)] = [username, password]#adds it to the table
        response = (
            supabase.table("USERS")
            .insert({"UserN": username, "PassW": password})
            .execute()
        )
        #adds it to the sql table
        return redirect(url_for("login"))# Goes to the login page
    
    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")# hash the password
        condition = (table_df['UserN'] == username) & (table_df['PassW'] == password)

        print(username)
        print(password)
# The line above gets the username and password into one variable in the same row 
        if table_df[condition].any(axis=None): #checks if the username or password is correct
            session['username'] = username #adds the username to a session dict
            #That allows for information to be shared in between pages
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    name = session.get('username')# Gets the username for the current session
    # All this is to add a button next to each token row
    # parses the stocks dataframe as an html table to add buttons easily
    html_table = bs.BeautifulSoup(df.to_html(classes='data')) 
    rows = html_table.find_all('tr') # Finds each row in the html table
    first = True # meant to skip the first row which is just headers
    for row in rows:
        if(first):
            tag = html_table.new_tag("td", text="New Cell")
            tag.string = "Buttons"
            row.append(tag)
            first = False

        else:
            first_tag = html_table.new_tag("button", type = "button")
            first_tag.string = "PRESS ME!"
            tag = html_table.new_tag('td', text='New Cell')
            tag.append(first_tag)
            row.append(tag)

    response = (supabase.table("CHOSEN") # Gets the user chosen stocks
        .select("*")
        .execute()
    )
    user_options = pd.DataFrame(response.data)
    actual_user = user_options.loc[user_options['UserN'] == name] # Gets the stock data of the current user
    if request.method == "POST": # Waits for the user to type a stock
        stock = request.form.get("stock")
        condition = (df['Ticker'] == stock)
        sCondition = (actual_user['Ticker'] == stock)
        # Checks if the stock exists and is not an already chosen stock
        if df[condition].any(axis=None) and not(actual_user[sCondition].any(axis = None)):
            response = (
                supabase.table("CHOSEN") # adds the stock to the table
                .upsert({"UserN": name, "Ticker": stock}, ignore_duplicates = True)
                .execute()
            )   
            
    return render_template("dashboard.html", username = name, tables=[html_table], titles=df.columns.values)
#Does it as a function call so that dashboard.html has the proper information to display everything

@app.route("/userStocks")
def userStocks():
    name = session.get('username')
    response = (supabase.table("CHOSEN") # Gets the user stock table
        .select("*")
        .execute()
    )
    user_options = pd.DataFrame(response.data)
    actual_user = user_options.loc[user_options['UserN'] == name] # Gets all the stocks of the current user

    return render_template("userStocks.html", username = name, tables = [actual_user.to_html()], titles= user_options.columns.values)

@app.route("/logout")
def logout():
    return redirect(url_for("login"))
#goes back to the login page if the logout button is pressed

if __name__ == "__main__": # Running the app in debug mode
    app.run(debug=True)




#def get_alpha_vantage_symbols(api_key): # Gets all the tickers from a website might have to figure out how to limit it
 #   url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
    
    # Download CSV data
  #  with requests.get(url) as r:
   #     data = r.content.decode('utf-8').split('\n')
    #    # Process and store symbols
     #   symbols = [line.split(',')[0] for line in data[1:] if line]
      #  return symbols
#tickers = get_alpha_vantage_symbols("PI5qAc7UFswiigQSOXmVmT6haKhG0it4")
#data = pd.DataFrame(columns=tickers) # Uses a pandas dataframe to hold all the symbol data
#for ticker in tickers: # Gets the ticker data from yfinance but I think it's too many tickers
 #   data[ticker] = yf.download(ticker, auto_adjust=False)['Adj Close']
#table = soup.find('table', attrs={'class': 'wikitable sortable', 'id': 'constituents'}) # Find the table that has the S&P 500 tickers
#table = soup.find('table', {'class': 'wikitable sortable'})
#df.to_csv('sp500_stocks.csv', mode='w+') # Putting it into a csv file for us to see
# Connecting to the server

#conn = mysql.connector.connect(user = 'root', # Connects to mydatabase
 #                              host = 'localhost',
  #                             passwd = 'YOUR PASSWORD',
   #     
#df.to_sql('TEST', conn, if_exists = 'replace', index = False)
#exit = False
#while not exit:
 #  choice = input("Do you want to add a user or login\n1 = add, 2 = login: ")

  # if choice == '1':
   #   username = input("Input username: ")
   #   password = input("Input password: ")
   #   condition = (table_df['UserN'] == username) & (table_df['PassW'] == password)

   #   if table_df[condition].any(axis=None):
    #     print("Username or Password already exists. please try again!")
   #   else:
    #    table_df.loc[len(table_df)] = [username, password]
    #    table_df.to_sql('USERS', conn, if_exists = 'replace', index = False)
 #  if choice == '2':
  #    username = input("Input username: ")
  #    password = input("Input password: ")
  #    condition = (table_df['UserN'] == username) & (table_df['PassW'] == password)

  #    if table_df[condition].any(axis=None):
   #      exit = True

  #    if exit == False:
   #      print("Wrong username or password please try again")
#print("Ayy you did it!")          

#s = bcrypt.gensalt() # need it to hash the password
#conn.close() # Disconnecting from the server      


