import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Title and description of the app
st.title("Stock Price Analysis for RELIANCE.NS")
st.write("""
This app fetches stock price data for RELIANCE.NS from Yahoo Finance, visualizes it with candlestick charts, calculates technical indicators (SMA and RSI), and provides key statistics.
""")

# Ticker symbol set to RELIANCE.NS
ticker = "RELIANCE.NS"

# Date range selection
default_start_date = pd.to_datetime("2022-01-01")
default_end_date = pd.to_datetime("today")
start_date = st.date_input("Start Date", value=default_start_date)
end_date = st.date_input("End Date", value=default_end_date)

# Fetch stock data
if ticker:
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    if not stock_data.empty:
        st.subheader(f"Candlestick Chart for {ticker.upper()} (Last 30 Days)")

        # Filter last 30 days of data
        last_30_days = stock_data[-30:]

        # Calculate SMAs
        stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['SMA_100'] = stock_data['Close'].rolling(window=100).mean()

        # Create candlestick chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=last_30_days.index,
                                      open=last_30_days['Open'],
                                      high=last_30_days['High'],
                                      low=last_30_days['Low'],
                                      close=last_30_days['Close'],
                                      name='Candlesticks'))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA_50'],
                                 mode='lines', name='SMA 50', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA_100'],
                                 mode='lines', name='SMA 100', line=dict(color='red')))
        
        fig.update_layout(title=f"{ticker.upper()} Candlestick Chart with SMAs",
                          xaxis_title="Date",
                          yaxis_title="Price",
                          template="plotly_dark")
        st.plotly_chart(fig)

        # Calculate average return and standard deviation of returns (last 90 days)
        stock_data['Return'] = stock_data['Close'].pct_change()
        last_90_days = stock_data[-90:]
        avg_return = last_90_days['Return'].mean()
        std_return = last_90_days['Return'].std()

        st.subheader("Key Statistics (Last 90 Days)")
        stats_table = pd.DataFrame({
            "Statistic": ["Average Return", "Standard Deviation of Return"],
            "Value": [f"{avg_return:.4f}", f"{std_return:.4f}"]
        })
        st.table(stats_table)

        # Calculate and display RSI chart
        stock_data['RSI'] = calculate_rsi(stock_data)
        st.subheader("Relative Strength Index (RSI) Chart")
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'],
                                      mode='lines', name='RSI', line=dict(color='orange')))
        rsi_fig.update_layout(title="RSI Chart",
                              xaxis_title="Date",
                              yaxis_title="RSI",
                              template="plotly_dark")
        st.plotly_chart(rsi_fig)

    else:
        st.error("No data found. Please check the date range.")
