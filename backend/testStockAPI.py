import yfinance as yf
import requests
import pandas as pd
#import mysql.connector
from sqlalchemy import create_engine # make sure to also pip install pymysql
import bs4 as bs
from flask import Flask

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

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15 Ddg/18.6'} # Make sure you change the user agent to fit your browser
resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies' , headers=headers) # Get the website information from wikipedia
soup = bs.BeautifulSoup(resp.text, 'lxml') # Parse it using beautiful soup to get the html information
#table = soup.find('table', attrs={'class': 'wikitable sortable', 'id': 'constituents'}) # Find the table that has the S&P 500 tickers
#table = soup.find('table', {'class': 'wikitable sortable'})
table = soup.find('table') # Find the table that has the S&P 500 tickers

tickers = []

for row in table.find_all('tr')[1:]: # tr is the table row and you skip that first row
    ticker = row.find_all('td')[0].text # td [0] gives you the first column which is the ticker name
    tickers.append(ticker) 

tickers = [s.replace('\n', '') for s in tickers] # Remove the newline character from each ticker name

data = yf.download(tickers, period ='1d', auto_adjust = False) # Get the full ticker information from yfinance
print(data.head())
df = data.stack().reset_index().rename(index=str, columns={"level_1": "Ticker"}).sort_values(['Ticker']) # Trying to make it look better and more organized

df = df.drop("Date", axis = 1)


print(df.head()) # Gets the tail end of all the data
df.to_csv('sp500_stocks.csv', mode='w+')
print(df.info())

# Connecting to the server

#conn = mysql.connector.connect(user = 'root', # Connects to mydatabase
 #                              host = 'localhost',
  #                             passwd = '',
   #                           database = 'STONKS')

#engine = create_engine('mysql+pymysql://root:YOURPASSWORD@localhost/STONKS')
#conn = engine.connect()

#print(conn)


#df.to_sql('TEST', conn, if_exists = 'replace', index = False)

#conn.close() # Disconnecting from the server

#app = Flask(__name__)
#@app.route("/stocks")

#def stocks():
 #   return data.to_dict()


#if __name__ == "__main__":
 #   app.run(debug=True)