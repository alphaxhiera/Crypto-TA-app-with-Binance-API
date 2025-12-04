import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================
# CoinGecko API with YOUR Key (Free tier = 10,000 calls/month)
# =====================================
API_KEY = st.secrets["coingecko_api_key"]  # We'll set this in secrets (see Step 3)

headers = {"x-cg-demo-api-key": API_KEY}  # Free tier header

@st.cache_data(ttl=60, show_spinner=False)
def get_data(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        return df.sort_values('timestamp').reset_index(drop=True)
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# =====================================
# Indicators + ATR
# =====================================
def add_indicators(df):
    df['sma10'] = df['close'].rolling(10).mean()
    df['sma30'] = df['close'].rolling(30).mean()

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + rs)) if (rs := gain / loss).replace([float('inf')], 0).isna().all() else 100 - (100 / (1 + rs))

    # MACD
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['signal']

    # Bollinger Bands
    df['bb_mid'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)

    # ATR for TP/SL
    df['tr'] = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()

    return df

# =====================================
# Analysis Engine
# =====================================
def generate_analysis(df):
    l = df.iloc[-1]
    p = df.iloc[-2]
    price = l['close']
    atr = l['atr'] if not pd.isna(l['atr']) else price * 0.02

    trend = "Bullish" if l['sma10'] > l['sma30'] else "Bearish"
    rsi_val = l['rsi']
    rsi_zone = "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral"

    score = 0
    if trend == "Bullish": score += 2
    if l['macd_hist'] > 0: score += 1
    if price > l['sma10']: score += 1
    if rsi_val < 65: score += 1

    if score >= 4:   rec, action = "STRONG BUY", "Enter Long Now"
    elif score == 3: rec, action = "BUY", "Consider Long"
    elif score <= 1: rec, action = "STRONG SELL", "Short or Exit"
    else:            rec, action = "HOLD", "Wait"

    return {
        "price": price,
        "trend": trend,
        "rsi": round(rsi_val, 2),
        "rsi_zone": rsi_zone,
        "score": score,
        "recommendation": rec,
        "action": action,
        "tp1": round(price + atr * 1.5, 6),
        "tp2": round(price + atr * 3, 6),
        "sl": round(price - atr * 1.5, 6),
        "resistance": df['high'].tail(30).max(),
        "support": df['low'].tail(30).min()
    }

# =====================================
# Streamlit App
# =====================================
st.set_page_config(page_title="Crypto TA Pro", layout="wide")
st.title("Crypto Technical Analysis Pro")
st.markdown("**Powered by CoinGecko API (Official Free Tier)**")

coins = {
    "Bitcoin": "bitcoin", "Ethereum": "ethereum", "BNB": "binancecoin",
    "Solana": "solana", "XRP": "ripple", "Cardano": "cardano",
    "Dogecoin": "dogecoin", "Avalanche": "avalanche-2", "Shiba Inu": "shiba-inu"
}

col1, col2 = st.columns([1, 3])
with col1:
    coin = st.selectbox("Coin", list(coins.keys()))
    days = st.selectbox("Period", [7, 14, 30, 90, 180, 365], index=2)

if st.button("Analyze Now", type="primary"):
    with st.spinner("Fetching data from CoinGecko..."):
        df = get_data(coins[coin], days)

    if df is None or len(df) < 50:
        st.error("Not enough data. Try longer period.")
        st.stop()

    df = add_indicators(df)
    analysis = generate_analysis(df)
    latest = df.iloc[-1]

    # Chart
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        subplot_titles=("Price + Indicators", "RSI", "MACD", "Volume Proxy"),
                        row_heights=[0.5, 0.15, 0.15, 0.2])

    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'],
                                 low=df['low'], close=df['close'], name="Price"), row=1, col=1)
    for line, name, color in [(df['sma10'], "SMA 10", "lime"), (df['sma30'], "SMA 30", "orange"),
                              (df['bb_upper'], "BB Upper", "gray"), (df['bb_lower'], "BB Lower", "gray")]:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=line, name=name,
                                 line=dict(color=color, dash="dot" if "BB" in name else "solid")), row=1, col=1)

    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    colors = ['green' if v >= 0 else 'red' for v in df['macd_hist']]
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['macd_hist'], name="MACD Hist", marker_color=colors), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['signal'], name="Signal", line=dict(color="orange")), row=3, col=1)

    fig.add_trace(go.Bar(x=df['timestamp'], y=(df['high']-df['low']), name="Vol Proxy", marker_color="lightblue"), row=4, col=1)

    fig.update_layout(height=900, title=f"{coin} • Last {days} days • Updated {latest['timestamp'].strftime('%Y-%m-%d %H:%M')} UTC")
    st.plotly_chart(fig, use_container_width=True)

    # Summary
    st.success(f"**SIGNAL: {analysis['recommendation']}** → {analysis['action']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Price", f"${analysis['price']:,.2f}")
    c2.metric("RSI", analysis['rsi'], delta=analysis['rsi_zone'])
    c3.metric("Score", f"{analysis['score']}/5")

    st.info(f"""
    **Trade Setup**  
    • Resistance → {analysis['resistance']:.6f}  
    • Support → {analysis['support']:.6f}  
    • Take Profit 1 → {analysis['tp1']}  
    • Take Profit 2 → {analysis['tp2']}  
    • Stop Loss → {analysis['sl']}  
    """)

    if "BUY" in analysis['recommendation']:
        st.balloons()

st.caption("CoinGecko API • Free tier • Not financial advice")
