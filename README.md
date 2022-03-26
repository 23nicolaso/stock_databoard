# What is the Stock Databoard
Scrapes and requests the technical and fundamental data of a given stock in a way that's easy to read

# What information is shown? 
Once you have logged in, the time, date, temperature, and CNBC headline of the day are shown. 

Next,you can fetch data for a specific ticker, which includes: 
news headlines, 
holder statistics, 
a description of the company, 
p/e ratio, 
market cap, 
dividend yield, 
earnings growth, 
beta, 
tradingview technical analysis signal, 
a chart of its price over time, 
RSI, ADX and PPO calculated over 14 day, 50 day and 300 day intervals respectively

# What are the dependencies using for the dashboard? 
The dashboard requires python 3, 

And uses the imports : Tkinter, matplotlib, yfinance, ta, tradingview_ta, ttk_themes, requests and bs4,
which can be installed with the following commands:

pip install tkinter
pip install matplotlib
pip install requests
pip install bs4
pip install ttkthemes
pip install ta
pip install yfinance
pip install tradingview_ta

# How can I run the dashboard? 
First get api keys from openweathermap.org/api, and alphavantage.co/support/#api-key. Next, set up config by replacing the phrases like your latitude and your api key with your latitude and api key. 

Finally, just run the stockdashboard.py file and enjoy! 
