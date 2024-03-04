import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
import pandas_ta as ta
import cufflinks as cf
from plotly.offline import iplot
import streamlit as st
import scipy.stats as sc


@st.cache_data
def get_tickers():
    df_nasdaq = pd.read_csv("Nasdaq_Tickers.csv")
    df_nyse = pd.read_csv("NYSE_Tickers.csv")

    df = pd.concat([df_nasdaq, df_nyse])

    df = df.drop_duplicates(subset="Symbol", keep="first")

    symbols = df["Symbol"].tolist()

    return symbols

@st.cache_data
def load_data(symbol, start_date, end_date):
    return yf.download(symbol, start=start_date, end=end_date)

st.sidebar.header("Stock Parameters")

ticker = st.sidebar.selectbox("Ticker", get_tickers())


end_date = st.sidebar.date_input("End Date", dt.date.today())
start_date = st.sidebar.date_input("Start Date", end_date - relativedelta(months=3))

if start_date > end_date:
    st.sidebar.error("Start date must fall before end date")

st.sidebar.header("TA Parameters")

volume = st.sidebar.checkbox(label="Add Volume")

exp_sma = st.sidebar.expander("SMA")
sma_flag = exp_sma.checkbox(label="Add Simple Moving Average")
sma_periods = exp_sma.number_input(label="SMA Periods", min_value=1, max_value=50, value=20, step=1)

exp_boll = st.sidebar.expander("Bollinger Bands")
bb_flag = exp_boll.checkbox(label="Add Bollinger Bands")
bb_periods = exp_boll.number_input(label="BB Periods", min_value=1, max_value=50, value=20, step=1)
bb_st_dev = exp_boll.number_input(label="# of St Dev", min_value=1, max_value=4, value=2, step=1)

exp_rsi = st.sidebar.expander("RSI")
rsi_flag = exp_rsi.checkbox(label="Add RSI")
rsi_upper = exp_rsi.number_input(label="RSI Upper", min_value=50, max_value=90, value=70, step=1)
rsi_lower = exp_rsi.number_input(label="RSI Lower", min_value=10, max_value=50, value=30, step=1)

exp_macd = st.sidebar.expander("MACD")
macd_flag = exp_macd.checkbox(label="Add MACD")
macd_fast = exp_macd.number_input(label="MACD Fast Period", min_value=5, max_value=20, value=12, step=1)
macd_slow = exp_macd.number_input(label="MACD Slow Period", min_value=20, max_value=35, value=26, step=1)
macd_signal = exp_macd.number_input(label="MACD Signal Period", min_value=5, max_value=12, value=9, step=1)

exp_metrics = st.sidebar.expander("Metrics")
show_metrics_flag = exp_metrics.checkbox(label="Add Metrics")
metrics_period = exp_metrics.number_input(label="Add Period For Calculated Metrics", min_value=5, max_value=90, value=30, step=1)

exp_market_metrics = st.sidebar.expander("Entire Market Metrics")
show_market_metrics_flag = exp_market_metrics.checkbox(label="Add Market Metrics")
market_metrics_period = exp_market_metrics.number_input(label="Add Period For Calculated Market Metrics", min_value=5, max_value=90, value=30, step=1)



st.title("TA Desktop App")

df = load_data(ticker, start_date, end_date)
pct_change = df["Adj Close"].pct_change().dropna()

title_string = f"{ticker}'s stock Price"


qf = cf.QuantFig(df, title=title_string)

if volume:
    qf.add_volume()
if sma_flag:
    qf.add_sma(periods=sma_periods)
if bb_flag:
    qf.add_bollinger_bands(periods=bb_periods, boll_std=bb_st_dev)
if rsi_flag:
    qf.add_rsi(rsi_upper=rsi_upper, rsi_lower=rsi_lower, showbands=True)
if macd_flag:
    qf.add_macd(fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)

fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)