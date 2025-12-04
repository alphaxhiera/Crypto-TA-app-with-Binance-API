import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from Binance API
def get_response(endpoint):
    url = "https://api.binance.com" + endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Add Simple Moving Averages (SMA)
def add_sma(df, window_short=10, window_long=30):
    df['sma_short'] = df['close'].rolling(window=window_short).mean()
    df['sma_long'] = df['close'].rolling(window=window_long).mean()
    return df

# Add Relative Strength Index (RSI)
def add_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# Add Moving Average Convergence Divergence (MACD)
def add_macd(df, fast=12, slow=26, signal=9):
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['signal_line'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['signal_line']
    return df

# Streamlit App Layout
st.title('Cryptocurrency Technical Analysis App (Binance API)')

# Dropdown for popular symbols
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
symbol = st.selectbox('Trading Pair', symbols)

# Interval selection
intervals = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
interval = st.selectbox('Interval', intervals, index=5)  # Default to 1d

# Limit selection (number of candles)
limit_options = [100, 250, 500, 1000]
limit = st.selectbox('Number of Candles (Limit)', limit_options, index=2)

if st.button('Analyze'):
    endpoint = f"/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = get_response(endpoint)
    if data:
        # Parse Binance response: list of [open_time, open, high, low, close, volume, ...]
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        # Convert to numeric and datetime
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp').reset_index(drop=True)

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=(f'{symbol} Candlestick with SMAs', 'RSI', 'MACD'),
                            row_heights=[0.5, 0.25, 0.25])

        # Candlestick trace
        fig.add_trace(go.Candlestick(x=df['timestamp'],
                                     open=df['open'],
                                     high=df['high'],
                                     low=df['low'],
                                     close=df['close'],
                                     name='OHLC'),
                      row=1, col=1)

        # SMA traces
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_short'], name='SMA Short (10)', line=dict(color='blue')),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_long'], name='SMA Long (30)', line=dict(color='orange')),
                      row=1, col=1)

        # RSI trace with overbought/oversold lines
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI (14)', line=dict(color='purple')),
                      row=2, col=1)
        fig.add_shape(type='line', x0=df['timestamp'].min(), x1=df['timestamp'].max(), y0=70, y1=70,
                      line=dict(color='red', dash='dash'), row=2, col=1)
        fig.add_shape(type='line', x0=df['timestamp'].min(), x1=df['timestamp'].max(), y0=30, y1=30,
                      line=dict(color='green', dash='dash'), row=2, col=1)

        # MACD traces
        hist_colors = ['green' if val >= 0 else 'red' for val in df['macd_histogram']]
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['macd_histogram'], name='MACD Histogram', marker_color=hist_colors),
                      row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name='MACD Line', line=dict(color='blue')),
                      row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['signal_line'], name='Signal Line', line=dict(color='red')),
                      row=3, col=1)

        # Layout updates
        period_text = f'{limit} {interval} candles'
        fig.update_layout(title=f'{symbol} Technical Analysis ({period_text})',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data (Last 10 Rows)')
        st.dataframe(df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(10))

        # Info on data range
        start_date = df['timestamp'].min().strftime('%Y-%m-%d %H:%M')
        end_date = df['timestamp'].max().strftime('%Y-%m-%d %H:%M')
        st.info(f'Data from {start_date} to {end_date} (UTC)')