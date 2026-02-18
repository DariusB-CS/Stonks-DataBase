import yfinance as yf
import requests
import pandas as pd
import mysql.connector

def get_alpha_vantage_symbols(api_key): # Gets all the tickers from a website might have to figure out how to limit it
    url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
    
    # Download CSV data
    with requests.get(url) as r:
        data = r.content.decode('utf-8').split('\n')
        # Process and store symbols
        symbols = [line.split(',')[0] for line in data[1:] if line]
        return symbols



# Connecting from the server
conn = mysql.connector.connect(user = 'root', # Connects to mydatabase
                               host = 'localhost',
                               passwd = 'YOURPASSWORD',
                              database = 'STONKS')
print(conn)

tickers = get_alpha_vantage_symbols("PI5qAc7UFswiigQSOXmVmT6haKhG0it4")
data = pd.DataFrame(columns=tickers) # Uses a pandas dataframe to hold all the symbol data

for ticker in tickers: # Gets the ticker data from yfinance but I think it's too many tickers
    data[ticker] = yf.download(ticker, auto_adjust=False)['Adj Close']

data.tail() # Gets the tail end of all the data

# Disconnecting from the server
conn.close()