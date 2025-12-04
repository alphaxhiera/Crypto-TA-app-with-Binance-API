import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name='MACD Line', line=dict(color='blue')),import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevityimport streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch data from CoinGecko API
def get_response(endpoint, api_key):
    headers = {"x-cg-demo-api-key": api_key}
    url = "https://api.coingecko.com/api/v3" + endpoint
    response = requests.get(url, headers=headers)
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
st.title('Cryptocurrency Technical Analysis App')

api_key = st.text_input('Enter your CoinGecko Demo API Key', type='password')
coin_id = st.text_input('Coin ID (e.g., bitcoin)', 'bitcoin')
days = st.selectbox('Data Range (Days)', [30, 60, 90, 180, 365, 'max'], index=2)

if api_key and st.button('Analyze'):
    endpoint = f"/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    data = get_response(endpoint, api_key)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('timestamp')

        # Compute indicators
        df = add_sma(df)
        df = add_rsi(df)
        df = add_macd(df)

        # Create interactive chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=('Candlestick with SMAs', 'RSI', 'MACD'),
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
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevity
                      row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['signal_line'], name='Signal Line', line=dict(color='red')),
                      row=3, col=1)

        # Layout updates
        fig.update_layout(title=f'{coin_id.upper()} Technical Analysis (Last {days} Days)',
                          xaxis_title='Date',
                          height=800,
                          showlegend=True,
                          xaxis_rangeslider_visible=True)

        st.plotly_chart(fig, use_container_width=True)

        # Display raw data table (optional)
        st.subheader('Raw OHLC Data')
        st.dataframe(df.tail(10))  # Show last 10 rows for brevity
