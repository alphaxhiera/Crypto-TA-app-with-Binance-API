import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ===================== CONFIG =====================
st.set_page_config(page_title="Crypto TA Pro", page_icon="Chart", layout="wide")

@st.cache_data(ttl=300, show_spinner="Fetching market data...")
def get_ohlc_data(coin_id: str, days: str, api_key: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}
    headers = {"x-cg-demo-api-key": api_key} if api_key else {}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return None

def add_indicators(df: pd.DataFrame):
    df = df.copy()
    df['sma_10'] = df['close'].rolling(10).mean()
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    df['sma_200'] = df['close'].rolling(200).mean()

    # RSI
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['signal']

    # Bollinger Bands
    df['bb_mid'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * 2)

    return df

# ===================== SMART ANALYSIS ENGINE =====================
def generate_technical_analysis(df, coin_name):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest['close']
    
    # Key Signals
    golden_cross = latest['sma_50'] > latest['sma_200'] and prev['sma_50'] <= prev['sma_200']
    death_cross = latest['sma_50'] < latest['sma_200'] and prev['sma_50'] >= prev['sma_200']
    
    macd_bullish = latest['macd'] > latest['signal'] and prev['macd'] <= prev['signal']
    macd_bearish = latest['macd'] < latest['signal'] and prev['macd'] >= prev['signal']
    
    rsi = latest['rsi']
    rsi_overbought = rsi > 70
    rsi_oversold = rsi < 30
    
    price_near_upper_bb = price > latest['bb_upper'] * 0.99
    price_near_lower_bb = price < latest['bb_lower'] * 1.01
    
    trend = "Strong Bullish" if latest['close'] > latest['sma_20'] > latest['sma_50'] > latest['sma_200'] else \
            "Strong Bearish" if latest['close'] < latest['sma_20'] < latest['sma_50'] < latest['sma_200'] else \
            "Bullish" if latest['close'] > latest['sma_20'] else \
            "Bearish" if latest['close'] < latest['sma_20'] else "Sideways/Consolidation"

    # Forecast & Take Profit Levels
    atr = (df['high'] - df['low']).rolling(14).mean().iloc[-1]
    resistance = df['high'].tail(50).max()
    support = df['low'].tail(50).min()

    tp1 = price * 1.05   # +5%
    tp2 = price * 1.10   # +10%
    tp3 = price * 1.20   # +20%
    stop_loss = price * 0.92  # -8%

    if trend.startswith("Bullish"):
        tp1 = max(tp1, resistance * 1.02)
        tp3 = resistance * 1.15
    elif trend.startswith("Bearish"):
        tp1 = price * 0.95
        tp2 = price * 0.90
        stop_loss = price * 1.08

    # Final Recommendation
    score = 0
    reasons = []

    if golden_cross: score += 3; reasons.append("Golden Cross (50/200 SMA)")
    if death_cross: score -= 3; reasons.append("Death Cross (50/200 SMA)")
    if macd_bullish: score += 2; reasons.append("MACD Bullish Crossover")
    if macd_bearish: score -= 2; reasons.append("MACD Bearish Crossover")
    if rsi < 30: score += 2; reasons.append("RSI Oversold → Reversal Likely")
    if rsi > 70: score -= 2; reasons.append("RSI Overbought → Pullback Risk")
    if price_near_lower_bb: score += 1; reasons.append("Price at Lower Bollinger → Bounce Possible")
    if price_near_upper_bb: score -= 1; reasons.append("Price at Upper Bollinger → Overextended")

    if score >= 5:
        signal = "STRONG BUY"
        color = "success"
    elif score >= 3:
        signal = "BUY"
        color = "success"
    elif score > -3:
        signal = "HOLD / WAIT"
        color = "warning"
    elif score > -5:
        signal = "SELL"
        color = "inverse"
    else:
        signal = "STRONG SELL"
        color = "inverse"

    return {
        "signal": signal,
        "color": color,
        "score": score,
        "reasons": reasons,
        "trend": trend,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "stop_loss": stop_loss,
        "support": support,
        "resistance": resistance,
        "rsi": rsi,
        "golden_cross": golden_cross,
        "death_cross": death_cross,
        "macd_bullish": macd_bullish,
        "macd_bearish": macd_bearish
    }

# ===================== UI =====================
st.title("Crypto Technical Analysis Pro")
st.markdown("### AI-Powered Signals • Forecast • Take Profit & Stop Loss")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("CoinGecko API Key", type="password", help="Free at coingecko.com/en/api")
    coin_options = {
        "Bitcoin": "bitcoin", "Ethereum": "ethereum", "BNB": "binancecoin",
        "Solana": "solana", "XRP": "ripple", "Dogecoin": "dogecoin",
        "Cardano": "cardano", "Avalanche": "avalanche-2", "Pepe": "pepe",
        "Shiba In env": "shiba-inu", "Toncoin": "toncoin"
    }
    coin_name = st.selectbox("Cryptocurrency", options=list(coin_options.keys()), index=0)
    coin_id = coin_options[coin_name]
    days = st.selectbox("Timeframe", ["30", "90", "180", "365", "max"], index=1)

if st.button("Analyze Now", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing {coin_name}..."):
        data = get_ohlc_data(coin_id, days, api_key or "demo")
        if not data:
            st.error("Failed to fetch data. Check API key or try again.")
            st.stop()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = add_indicators(df).dropna()

        analysis = generate_technical_analysis(df, coin_name)
        latest = df.iloc[-1]
        price = latest['close']

        # ===================== MAIN DASHBOARD =====================
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Price", f"${price:,.2f}")
        with col2:
            st.metric("RSI (14)", f"{analysis['rsi']:.1f}")
        with col3:
            st.metric("Trend", analysis['trend'])
        with col4:
            st.markdown(f"### **{analysis['signal']}**")
            st.markdown(f"<span style='color:{'green' if 'BUY' in analysis['signal'] else 'red' if 'SELL' in analysis['signal'] else 'orange'}'>Score: {analysis['score']}/10</span>", unsafe_allow_html=True)

        # Signal Reasons
        st.success("**Why This Signal?**")
        for reason in analysis['reasons']:
            st.write("• " + reason)

        # Plot
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            subplot_titles=(f"{coin_name} Candlestick + Indicators", "RSI", "MACD", "Bollinger Bands"),
                            row_heights=[0.45, 0.15, 0.2, 0.2])

        # Candlestick + SMAs + BB
        fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_20'], name="SMA 20", line=dict(color="orange")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_50'], name="SMA 50", line=dict(color="blue")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_upper'], name="BB Upper", line=dict(color="gray", dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_lower'], name="BB Lower", line=dict(color="gray", dash="dot")), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        colors = ['green' if x >= 0 else 'red' for x in df['macd_hist']]
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['macd_hist'], name="Histogram", marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['signal'], name="Signal", line=dict(color="red")), row=3, col=1)

        fig.update_layout(height=1000, title=f"{coin_name} - Full Technical Analysis", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # ===================== ACTIONABLE RECOMMENDATIONS =====================
        st.markdown("## Actionable Trade Plan")

        if "BUY" in analysis['signal']:
            st.success(f"**Recommendation: {analysis['signal']} {coin_name}**")
            st.write(f"**Take Profit Levels:**")
            st.write(f"• TP1: `${analysis['tp1']:,.2f}` (+5% or next resistance)")
            st.write(f"• TP2: `${analysis['tp2']:,.2f}` (+10%)")
            st.write(f"• TP3: `${analysis['tp3']:,.2f}` (+20% moon target)")
            st.write(f"**Stop Loss:** `${analysis['stop_loss']:,.2f}` (-8%)")
            st.write(f"**Key Support:** `${analysis['support']:,.2f}`")

        elif "SELL" in analysis['signal']:
            st.error(f"**Recommendation: {analysis['signal']} or Short {coin_name}**")
            st.write("Consider taking profits or shorting until support breaks.")

        else:
            st.warning("**HOLD** – Wait for clearer signal. Market is indecisive.")

        st.caption("Not financial advice • Trade at your own risk • Generated automatically from technical indicators")
