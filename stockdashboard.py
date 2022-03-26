#!/bin/env python
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
from ttkthemes import ThemedStyle
import matplotlib.pyplot as plt
from ta.trend import *
from ta.momentum import *
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import config


# Application Themes
dark_mode, light_mode = ['equilux', 'dark_background'], ['yaru', 'ggplot']
if config.use_dark_theme:
    mode = dark_mode
else:
    mode = light_mode


def simple_get(url):
    """

    Attempts to get the content at `url` by making an HTTP GET request.

    If the content-type of response is some kind of HTML/XML, return the

    text content, otherwise return None.

    """

    try:

        with closing(get(url, stream=True)) as resp:

            if is_good_response(resp):

                return resp.content

            else:

                return None



    except RequestException as e:

        log_error('Error during requests to {0} : {1}'.format(url, str(e)))

        return None


def is_good_response(resp):
    """

    Returns True if the response seems to be HTML, False otherwise.

    """

    content_type = resp.headers['Content-Type'].lower()

    return (resp.status_code == 200

            and content_type is not None

            and content_type.find('html') > -1)


def log_error(e):
    """

    It is always a good idea to log errors.

    This function just prints them, but you can

    make it do anything.

    """

    print(e)


# Download Weather Data
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" %\
      (config.lat, config.lon, config.api_key)
response = get(url)
data = json.loads(response.text)
temperature = data["current"]["temp"]

# Find CNBC headline of the day
url = 'https://www.cnbc.com/world/?region=world'
raw_html = simple_get(url)
html = BeautifulSoup(raw_html, 'html.parser')
headline = html.find('div', class_="MarketsBanner-teaser").text

# Set up tkinter window
window = tk.Tk()
window.title("Login to dashboard")

# THEMES FOR AESTHETICS
style = ThemedStyle(window)

style.set_theme(mode[0])

plt.style.use(mode[1])

date = str(datetime.now()).split(" ")
short_time = tk.StringVar(value=datetime.now().strftime("%H:%M:%S"))

# Defining TTK Frames
login_frame = ttk.Frame(window)
main_frame = ttk.Frame(window)
results_frame = ttk.Frame(window)
summary_frame = ttk.Frame(window)
plot_frame = ttk.Frame(window)

# Create and grid login frame UI
app_label = ttk.Label(login_frame, text="Login To Dashboard", font=("", 30))
app_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="W")
username_label = ttk.Label(login_frame, text="Username:")
password_label = ttk.Label(login_frame, text="Password:")
username_entry = ttk.Entry(login_frame)
password_entry = ttk.Entry(login_frame, show="*")
username_label.grid(row=1, column=0, padx=5)
username_entry.grid(row=1, column=1, padx=5)
password_label.grid(row=2, column=0, padx=5)
password_entry.grid(row=2, column=1, padx=5)

# Create and grid dashboard base elements
dash_board_title = ttk.Label(main_frame, text="Stock Dashboard", font=("", 40))
dash_board_title.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
date_text = ttk.Label(main_frame, text=date[0], font=("", 20))
date_text.grid(row=1, column=0, padx=5, pady=5, sticky="W")
shorter_time_text = ttk.Label(main_frame, textvariable=short_time, font=("", 20))
shorter_time_text.grid(row=1, column=1, padx=5, pady=5, sticky="W")
headline_label = ttk.Label(main_frame, text=headline, font=("", 15), wraplength=400)
headline_label.grid(row=2, column=0, padx=5, pady=5, sticky="W", columnspan=3)
weather_label = ttk.Label(main_frame, text="Temperature: " + str(temperature))
weather_label.grid(row=1, column=2, sticky="W", padx=5)
ticker_entry = ttk.Entry(main_frame)
ticker_entry.grid(row=7, column=0, sticky="WE", padx=5, pady=5, columnspan=2)


# Functions below used a switch statements
# Color based on the how strong the TA signals are #D2222D = bearish, weak trend, #007000 = bullish, strong trend
# If data unavailable, displays N/A in neutral color
def choose_color(x):
    return {
        'STRONG_SELL': '#D2222D',
        'SELL': '#FFBF00',
        'BUY': '#238823',
        'STRONG_BUY': '#007000',
        'NEUTRAL': '#A8AAAA'
    }[x]


def rsi_color(x):
    if x != "N/A":
        if x >= 70: return '#D2222D'
        if x <= 30: return '#007000'
        if 30 < x < 70: return '#A8AAAA'
    else:
        return '#A8AAAA'


def adx_color(x):
    if x != "N/A":
        if x >= 75: return '#007000'
        if 50 <= x < 75: return '#238823'
        if 25 <= x < 50: return '#FFBF00'
        if x < 25: return '#D2222D'
    else:
        return '#A8AAAA'


def ppo_color(x):
    if x != "N/A":
        if x >= 50: return '#D2222D'
        if 0 < x < 50: return '#238823'
        if -50 < x <= 0: return '#FFBF00'
        if x <= -50: return '#007000'
    else:
        return '#A8AAAA'


def update_time():
    short_time.set(datetime.now().strftime("%H:%M:%S"))
    window.after(1, update_time)


def get_ticker_info():
    clear_frames(results_frame)
    clear_frames(summary_frame)
    clear_frames(plot_frame)

    ticker = ticker_entry.get()
    yahoo_finance_ticker = yf.Ticker(ticker)

    # Fetch and process ticker data
    overview = get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + ticker + '&apikey=' + config.aa_api)
    ticker_overview = overview.json()
    exchange = ticker_overview["Exchange"]
    desc = ticker_overview["Description"]
    peratio = ticker_overview["PERatio"]
    marketcap = ticker_overview["MarketCapitalization"]
    divyield = ticker_overview["DividendYield"]
    earningsgrowth = ticker_overview["QuarterlyEarningsGrowthYOY"]
    beta = ticker_overview["Beta"]

    # Create and grid UI Ticker summary
    section_title_label = ttk.Label(summary_frame, text="Ticker Summary", font=("", 30))
    section_title_label.grid(row=0, column=0, padx=5, pady=5)
    desc_label = ttk.Label(summary_frame, text=desc, wraplength=600, justify="left")
    desc_label.grid(row=0, column=1, columnspan=4, padx=5, pady=5)
    peratio_label = ttk.Label(summary_frame, text="P/E ratio: " + peratio)
    peratio_label.grid(row=1, column=0, padx=5, pady=5)
    marketcap_label = ttk.Label(summary_frame, text="Market Cap: " + marketcap)
    marketcap_label.grid(row=1, column=1, padx=5, pady=5)
    divyield_label = ttk.Label(summary_frame, text="Dividend Yield: " + divyield)
    divyield_label.grid(row=1, column=2, padx=5, pady=5)
    earningsgrowth_label = ttk.Label(summary_frame, text="Earnings Growth: " + earningsgrowth)
    earningsgrowth_label.grid(row=1, column=3, padx=5, pady=5)
    beta_label = ttk.Label(summary_frame, text="Beta: " + beta)
    beta_label.grid(row=1, column=4, padx=5, pady=5)

    # Get historical prices and make plot in plot_frame
    price_history = yahoo_finance_ticker.history(period="5y")
    fig = plt.figure(figsize=(5, 3))
    fig.add_subplot(111).plot(price_history['Close'])
    canvas = FigureCanvasTkAgg(fig, plot_frame)
    canvas._tkcanvas.pack(fill=tk.BOTH, expand=1)

    # Get yahoo finance recommendations
    news = yahoo_finance_ticker.news
    news_title_label = ttk.Label(results_frame, text="News Headlines", font=("", 30))
    news_title_label.grid(row=4, column=0, columnspan=5, padx=5, pady=5, sticky="WE")

    for i in range(5):
        title = news[i]['title']
        title_label = ttk.Label(results_frame, text=title, font=("", 10), wraplength=400)
        title_label.grid(row=5 + i, column=0, columnspan=5, padx=5, pady=5, sticky="W")

    url = "https://finance.yahoo.com/quote/" + ticker + "/holders?p=" + ticker
    raw_html = get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(raw_html.text, 'html.parser')

    table = soup.find_all('tr')
    processed_table_holders = list(map(lambda x: x.text, table))
    holders_label = ttk.Label(results_frame, text="Holder Statistics", font=("", 30))
    holders_label.grid(row=9, column=0, columnspan=5, padx=5, pady=5, sticky="WE")
    holder_1 = ttk.Label(results_frame, text=processed_table_holders[0], font=("", 10))
    holder_1.grid(row=10, column=0, padx=5, pady=5, columnspan=3, sticky="W")
    holder_2 = ttk.Label(results_frame, text=processed_table_holders[1], font=("", 10))
    holder_2.grid(row=11, column=0, padx=5, pady=5, columnspan=3, sticky="W")
    holder_3 = ttk.Label(results_frame, text=processed_table_holders[3], font=("", 10))
    holder_3.grid(row=12, column=0, padx=5, pady=5, columnspan=3, sticky="W")

    close = price_history['Close']

    try:
        short_rsi = round(rsi(close, window=14).iloc[-1], 2)
        mid_rsi = round(rsi(close, window=50).iloc[-1], 2)
        long_rsi = round(rsi(close, window=300).iloc[-1], 2)
        short_adx = round(adx(price_history['High'], price_history['Low'], close, 14).iloc[-1], 2)
        mid_adx = round(adx(price_history['High'], price_history['Low'], close, 50).iloc[-1], 2)
        long_adx = round(adx(price_history['High'], price_history['Low'], close, 300).iloc[-1], 2)
        short_ppo = round(ppo(close, window_slow=14, window_fast=5, window_sign=1).iloc[-1], 2)
        mid_ppo = round(ppo(close, window_slow=50, window_fast=14, window_sign=1).iloc[-1], 2)
        long_ppo = round(ppo(close, window_slow=300, window_fast=14, window_sign=1).iloc[-1], 2)
    except IndexError as error:
        short_rsi = mid_rsi = long_rsi = short_adx = mid_adx = long_adx = short_ppo = mid_ppo = long_ppo = "N/A"
    except Exception as exception:
        short_rsi = mid_rsi = long_rsi = short_adx = mid_adx = long_adx = short_ppo = mid_ppo = long_ppo = "N/A"

    ttk.Label(results_frame, text="RSI", font=("", 15)).grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(results_frame, text="ADX", font=("", 15)).grid(row=1, column=0, padx=5, pady=5)
    ttk.Label(results_frame, text="PPO", font=("", 15)).grid(row=2, column=0, padx=5, pady=5)
    ttk.Label(results_frame, text=str(short_rsi), font=("", 15), foreground=rsi_color(short_rsi)).grid(row=0, column=1,
                                                                                                       padx=5, pady=5)
    ttk.Label(results_frame, text=str(mid_rsi), font=("", 15), foreground=rsi_color(mid_rsi)).grid(row=0, column=2,
                                                                                                   padx=5, pady=5)
    ttk.Label(results_frame, text=str(long_rsi), font=("", 15), foreground=rsi_color(long_rsi)).grid(row=0, column=3,
                                                                                                     padx=5, pady=5)
    ttk.Label(results_frame, text=str(short_adx), font=("", 15), foreground=adx_color(short_adx)).grid(row=1, column=1,
                                                                                                       padx=5, pady=5)
    ttk.Label(results_frame, text=str(mid_adx), font=("", 15), foreground=adx_color(mid_adx)).grid(row=1, column=2,
                                                                                                   padx=5, pady=5)
    ttk.Label(results_frame, text=str(long_adx), font=("", 15), foreground=adx_color(long_adx)).grid(row=1, column=3,
                                                                                                     padx=5, pady=5)
    ttk.Label(results_frame, text=str(short_ppo), font=("", 15), foreground=ppo_color(short_ppo)).grid(row=2, column=1,
                                                                                                       padx=5, pady=5)
    ttk.Label(results_frame, text=str(mid_ppo), font=("", 15), foreground=ppo_color(mid_ppo)).grid(row=2, column=2,
                                                                                                   padx=5, pady=5)
    ttk.Label(results_frame, text=str(long_ppo), font=("", 15), foreground=ppo_color(long_ppo)).grid(row=2, column=3,
                                                                                                     padx=5, pady=5)

    stock_daily = TA_Handler(
        symbol=ticker,
        screener="america",
        exchange=exchange,
        interval=Interval.INTERVAL_1_DAY,
    )
    stock_hourly = TA_Handler(
        symbol=ticker,
        screener="america",
        exchange=exchange,
        interval=Interval.INTERVAL_1_HOUR,
    )
    stock_weekly = TA_Handler(
        symbol=ticker,
        screener="america",
        exchange=exchange,
        interval=Interval.INTERVAL_1_WEEK,
    )
    daily_rec = stock_daily.get_analysis().summary['RECOMMENDATION']
    daily_rec_label = ttk.Label(summary_frame, text="Daily Ta Signal:" + daily_rec, foreground=choose_color(daily_rec))
    daily_rec_label.grid(row=2, column=1, padx=5, pady=5)

    hourly_rec = stock_hourly.get_analysis().summary['RECOMMENDATION']
    hourly_rec_label = ttk.Label(summary_frame, text="Hourly Ta Signal:" + hourly_rec,
                                 foreground=choose_color(hourly_rec))
    hourly_rec_label.grid(row=2, column=2, padx=5, pady=5)

    weekly_rec = stock_weekly.get_analysis().summary['RECOMMENDATION']
    weekly_rec_label = ttk.Label(summary_frame, text="Weekly Ta Signal:" + weekly_rec,
                                 foreground=choose_color(weekly_rec))
    weekly_rec_label.grid(row=2, column=3, padx=5, pady=5)

    # Example output: {"RECOMMENDATION": "BUY", "BUY": 8, "NEUTRAL": 6, "SELL": 3}
    results_frame.grid(row=1, column=0, sticky="NSEW")
    summary_frame.grid(row=0, column=1, sticky="NSEW")
    plot_frame.grid(row=1, column=1, sticky="NSEW")


submit_ticker = ttk.Button(main_frame, text="Fetch Ticker", command=get_ticker_info)
submit_ticker.grid(row=7, column=2, sticky="WE", padx=5, pady=5)


def appinit():
    # Clear Window
    login_frame.grid_forget()
    main_frame.grid(row=0, column=0)

    update_time()


def attempt_login():
    if [username_entry.get(), password_entry.get()] in config.accounts:
        messagebox.showinfo("Login", "Login Successful")
        appinit()

    else:
        messagebox.showinfo("Login", "Incorrect Username or Password")


def clear_frames(frame):
    for widget in frame.winfo_children():
        widget.destroy()


login_button = ttk.Button(login_frame, text="Login", command=attempt_login)
login_button.grid(row=3, column=0, columnspan=2, sticky="WE", padx=5, pady=5)
login_frame.grid(row=0, column=0)

tk.mainloop()
