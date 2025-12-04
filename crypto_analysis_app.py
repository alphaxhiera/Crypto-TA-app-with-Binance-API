import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =====================================
# CoinGecko Data (Free & No API Key Needed)
# =====================================
@st.cache_data(ttl=60)  # Refresh every 60 seconds
def get_coingecko_data(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    try:
        data = requests.get(url, timeout=10).json()
        if not data:
            st.error("No data returned. Check coin ID.")
            return None
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        return df.sort_values('timestamp').reset_index(drop=True)
    except Exception as e:
        st.error(f"CoinGecko Error: {e}")
        return None

# =====================================
# Indicators
# =====================================
def add_indicators(df):
    df['sma10'] = df['close'].rolling(10).mean()
    df['sma30'] = df['close'].rolling(30).mean()

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

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

    # Simple ATR approximation
    df['tr'] = pd.concat([df['high'] - df['low'], 
                          (df['high'] - df['close'].shift()).abs(), 
                          (df['low'] - df['close'].shift()).abs()], axis=1).max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()

    return df

# =====================================
# Smart Analysis & Recommendation
# =====================================
def generate_analysis(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest['close']
    atr = latest['atr'] if not pd.isna(latest['atr']) else (price * 0.02)

    # Trend
    trend = "Bullish" if latest['sma10'] > latest['sma30'] else "Bearish"

    # RSI Zone
    rsi_val = latest['rsi']
    if rsi_val > 70:
        rsi_zone = "Overbought"
    elif rsi_val < 30:
        rsi_zone = "Oversold"
    else:
        rsi_zone = "Neutral"

    # MACD Signal
    macd_sig = "Bullish" if latest['macd_hist'] > 0 and prev['macd_hist'] <= 0 else \
               "Bearish" if latest['macd_hist'] < 0 and prev['macd_hist'] >= 0 else "Neutral"

    # Score (0–5)
    score = 0
    if trend == "Bullish": score += 2
    if latest['macd_hist'] > 0: score += 1
    if price > latest['sma10']: score += 1
    if rsi_val < 65: score += 1

    # Recommendation
    if score >= 4:
        rec = "STRONG BUY"
        action = "Enter Long Now"
    elif score == 3:
        rec = "BUY"
        action = "Consider Long"
    elif score <= 1:
        rec = "STRONG SELL"
        action = "Short or Stay Away"
    else:
        rec = "HOLD / WAIT"
        action = "Wait for confirmation"

    # Targets
    tp1 = round(price + atr * 1.5, 6)
    tp2 = round(price + atr * 3, 6)
    sl = round(price - atr * 1.5, 6)

    resistance = df['high'].tail(30).max()
    support = df['low'].tail(30).min()

    return {
        "price": price,
        "trend": trend,
        "rsi": round(rsi_val, 2),
        "rsi_zone": rsi_zone,
        "macd_sig": macd_sig,
        "score": score,
        "recommendation": rec,
        "action": action,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "resistance": resistance,
        "support": support
    }

# =====================================
# Streamlit App
# =====================================
st.set_page_config(page_title="Crypto TA Pro • CoinGecko", layout="wide")
st.title("Crypto Technical Analysis Pro")
st.markdown("**Live data from CoinGecko • Free & No API Key**")

# Popular coins (CoinGecko IDs)
coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "BNB": "binancecoin",
    "Solana": "solana",
    "Cardano": "cardano",
    "XRP": "ripple",
    "Dogecoin": "dogecoin",
    "Polkadot": "polkadot",
    "Avalanche": "avalanche-2",
    "Shiba Inu": "shiba-inu"
}

col1, col2 = st.columns([1, 3])
with col1:
    coin_name = st.selectbox("Select Coin", options=list(coins.keys()), index=0)
    coin_id = coins[coin_name]
    days = st.selectbox("Time Range", [7, 14, 30, 90, 180, 365], index=2)

if st.button("Analyze Now", type="primary"):
    with st.spinner(f"Fetching {coin_name} data from CoinGecko..."):
        df = get_coingecko_data(coin_id, days)
    
    if df is None or len(df) < 50:
        st.error("Not enough data. Try a longer time range.")
        st.stop()

    df = add_indicators(df)
    analysis = generate_analysis(df)
    latest = df.iloc[-1]

    # === Chart ===
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("Price & Indicators", "RSI (14)", "MACD", "Volume (Approx)"),
        row_heights=[0.5, 0.15, 0.15, 0.2]
    )

    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'],
                                 low=df['low'], close=df['close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma10'], name="SMA 10", line=dict(color="lime")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma30'], name="SMA 30", line=dict(color="orange")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_upper'], name="BB Upper", line=dict(dash="dot", color="gray")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_lower'], name="BB Lower", line=dict(dash="dot", color="gray")), row=1, col=1)

    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    colors = ['green' if v >= 0 else 'red' for v in df['macd_hist']]
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['macd_hist'], name="MACD Hist", marker_color=colors), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['signal'], name="Signal", line=dict(color="orange")), row=3, col=1)

    # Volume not available → fake from price movement
    volume_proxy = (df['high'] - df['low']).abs()
    fig.add_trace(go.Bar(x=df['timestamp'], y=volume_proxy, name="Vol Proxy", marker_color="lightblue"), row=4, col=1)

    fig.update_layout(height=900, showlegend=True,
                      title=f"{coin_name} ({coin_id.upper()}) • Last {days} Days")
    st.plotly_chart(fig, use_container_width=True)

    # === Summary ===
    st.markdown("## Trade Recommendation")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Price", f"${analysis['price']:,.2f}")
    with c2:
        st.metric("RSI", analysis['rsi'], delta=analysis['rsi_zone'])
    with c3:
        st.metric("Trend Score", f"{analysis['score']}/5", delta=analysis['recommendation'])

    st.success(f"**Signal: {analysis['recommendation']}**")
    st.info(f"**Action → {analysis['action']}**")

    st.markdown(f"""
    **Key Levels**  
    • Resistance: `{analysis['resistance']:.6f}`  
    • Support: `{analysis['support']:.6f}`  
    • Take Profit 1: `{analysis['tp1']}`  
    • Take Profit 2: `{analysis['tp2']}`  
    • Stop Loss: `{analysis['sl']}`  
    """)

    if analysis['recommendation'] in ["STRONG BUY", "BUY"]:
        st.balloons()

st.caption("Data: CoinGecko API • Educational tool • Not financial advice • DYOR")
