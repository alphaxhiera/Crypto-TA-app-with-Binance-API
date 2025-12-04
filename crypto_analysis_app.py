# File: crypto_ta_pro.py
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Crypto TA Pro", page_icon="Chart", layout="wide")

# ===================== DATA FETCH (PAKAI MARKET_CHART → SELALU ADA DATA) =====================
@st.cache_data(ttl=600, show_spinner="Mengambil data harga dari CoinGecko...")
def get_price_data(coin_id: str, days: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            st.error(f"Error {response.status_code}: CoinGecko sedang rate-limit atau coin tidak ditemukan.")
            return None
            
        data = response.json()["prices"]
        if not data:
            return None
            
        df = pd.DataFrame(data, columns=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        # Buat OHLC sederhana dari harga penutup harian (cukup akurat untuk TA)
        df["open"] = df["close"].shift(1)
        df["high"] = df[["open", "close"]].max(axis=1)
        df["low"] = df[["open", "close"]].min(axis=1)
        df.loc[0, "open"] = df.loc[0, "close"]  # Fix baris pertama
        
        return df[["timestamp", "open", "high", "low", "close"]]
        
    except Exception as e:
        st.error(f"Koneksi error: {e}")
        return None

# ===================== INDIKATOR =====================
def add_indicators(df: pd.DataFrame):
    df = df.copy()
    df["sma_10"] = df["close"].rolling(10).mean()
    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["sma_200"] = df["close"].rolling(200).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["signal"]

    # Bollinger Bands
    df["bb_mid"] = df["close"].rolling(20).mean()
    df["bb_std"] = df["close"].rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + (df["bb_std"] * 2)
    df["bb_lower"] = df["bb_mid"] - (df["bb_std"] * 2)

    return df

# ===================== ANALISIS OTOMATIS =====================
def generate_analysis(df, coin_name):
    if len(df) < 50:
        return {"signal": "DATA KURANG", "trend": "Tidak cukup data", "reasons": ["Perlu minimal 50 hari data"]}

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest["close"]

    # Signal detection
    golden_cross = latest["sma_50"] > latest["sma_200"] and prev["sma_50"] <= prev["sma_200"]
    death_cross = latest["sma_50"] < latest["sma_200"] and prev["sma_50"] >= prev["sma_200"]
    macd_bull = latest["macd"] > latest["signal"] and prev["macd"] <= prev["signal"]
    macd_bear = latest["macd"] < latest["signal"] and prev["macd"] >= prev["signal"]

    rsi_val = latest["rsi"]
    overbought = rsi_val > 70
    oversold = rsi_val < 30

    # Trend
    if latest["close"] > latest["sma_20"] > latest["sma_50"] > latest["sma_200"]:
        trend = "Strong Bullish"
    elif latest["close"] < latest["sma_20"] < latest["sma_50"] < latest["sma_200"]:
        trend = "Strong Bearish"
    elif latest["close"] > latest["sma_20"]:
        trend = "Bullish"
    elif latest["close"] < latest["sma_20"]:
        trend = "Bearish"
    else:
        trend = "Sideways"

    # Scoring
    score = 0
    reasons = []
    if golden_cross: score += 4; reasons.append("Golden Cross (50/200)")
    if death_cross: score -= 4; reasons.append("Death Cross (50/200)")
    if macd_bull: score += 2; reasons.append("MACD Bullish Crossover")
    if macd_bear: score -= 2; reasons.append("MACD Bearish Crossover")
    if oversold: score += 2; reasons.append(f"RSI Oversold ({rsi_val:.1f})")
    if overbought: score -= 2; reasons.append(f"RSI Overbought ({rsi_val:.1f})")
    if price < latest["bb_lower"]: score += 1; reasons.append("Harga di Lower Bollinger")
    if price > latest["bb_upper"]: score -= 1; reasons.append("Harga di Upper Bollinger")

    # Final signal
    if score >= 5:
        signal = "STRONG BUY"
        color = "success"
    elif score >= 3:
        signal = "BUY"
        color = "success"
    elif score > -2:
        signal = "HOLD"
        color = "warning"
    elif score > -5:
        signal = "SELL"
        color = "inverse"
    else:
        signal = "STRONG SELL"
        color = "inverse"

    # Take Profit & Stop Loss
    resistance = df["high"].tail(60).max()
    support = df["low"].tail(60).min()
    tp1 = round(price * 1.06, 2)
    tp2 = round(price * 1.12, 2)
    tp3 = round(price * 1.25, 2)
    sl = round(price * 0.92, 2)

    return {
        "signal": signal, "color": color, "score": score, "reasons": reasons,
        "trend": trend, "price": price, "rsi": rsi_val,
        "tp1": tp1, "tp2": tp2, "tp3": tp3, "sl": sl,
        "support": support, "resistance": resistance,
        "golden_cross": golden_cross, "death_cross": death_cross
    }

# ===================== UI =====================
st.title("Crypto Technical Analysis Pro")
st.markdown("**AI-Powered Signal • Forecast • Take Profit & Stop Loss** — 100% Grat, tanpa API key!")

with st.sidebar:
    st.header("Pilih Koin & Periode")
    coins = {
        "Bitcoin": "bitcoin", "Ethereum": "ethereum", "BNB": "binancecoin",
        "Solana": "solana", "XRP": "ripple", "Cardano": "cardano",
        "Dogecoin": "dogecoin", "Shiba Inu": "shiba-inu", "Pepe": "pepe",
        "Avalanche": "avalanche-2", "Toncoin": "toncoin", "TRON": "tron"
    }
    coin_name = st.selectbox("Cryptocurrency", options=list(coins.keys()))
    coin_id = coins[coin_name]
    
    period = st.selectbox("Periode", ["30", "90", "180", "365", "max"], index=2)

if st.button("Analyze Sekarang", type="primary", use_container_width=True):
    with st.spinner(f"Menganalisis {coin_name}..."):
        df_raw = get_price_data(coin_id, period)
        
        if df_raw is None or df_raw.empty:
            st.error(f"Tidak bisa mengambil data untuk {coin_name}. Coba coin lain.")
            st.stop()

        df = add_indicators(df_raw)
        df_valid = df.dropna()
        if df_valid.empty:
            df_valid = df.tail(100)  # fallback

        result = generate_analysis(df_valid, coin_name)
        latest_price = df_valid.iloc[-1]["close"]

        # ===================== DASHBOARD =====================
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Harga Saat Ini", f"${latest_price:,.2f}")
        with col2:
            st.metric("RSI (14)", f"{result['rsi']:.1f}")
        with col3:
            st.metric("Trend", result['trend'])
        with col4:
            st.markdown(f"### **{result['signal']}**")
            st.caption(f"Score: {result['score']}/10")

        if result["reasons"]:
            st.success("**Alasan Signal:**")
            for r in result["reasons"]:
                st.write("• " + r)

        # Chart
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            subplot_titles=("Candlestick + SMA + Bollinger", "RSI", "MACD", "Volume Proxy"),
                            row_heights=[0.5, 0.15, 0.2, 0.15])

        # Candlestick + SMA + BB
        fig.add_trace(go.Candlestick(x=df_valid['timestamp'], open=df_valid['open'],
                                     high=df_valid['high'], low=df_valid['low'], close=df_valid['close'],
                                     name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_20'], name="SMA 20", line=dict(color="orange")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_50'], name="SMA 50", line=dict(color="blue")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['bb_upper'], name="BB Upper", line=dict(dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['bb_lower'], name="BB Lower", line=dict(dash="dot")), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        colors = ['green' if v >= 0 else 'red' for v in df_valid['macd_hist']]
        fig.add_trace(go.Bar(x=df_valid['timestamp'], y=df_valid['macd_hist'], name="Histogram", marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['signal'], name="Signal", line=dict(color="red")), row=3, col=1)

        fig.update_layout(height=900, title=f"{coin_name} - Analisis Teknikal Otomatis", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # ===================== REKOMENDASI TRADING =====================
        st.markdown("## Trade Plan Otomatis")
        if "BUY" in result["signal"]:
            st.success(f"**REKOMENDASI: {result['signal']} {coin_name}**")
            st.write(f"**Take Profit:**")
            st.write(f"• TP1 → `${result['tp1']}` (+6%)")
            st.write(f"• TP2 → `${result['tp2']}` (+12%)")
            st.write(f"• TP3 → `${result['tp3']}` (+25%)")
            st.write(f"**Stop Loss:** `${result['sl']}` (-8%)")
            st.write(f"**Support:** `${result['support']:.2f}` | **Resistance:** `${result['resistance']:.2f}`")

        elif "SELL" in result["signal"]:
            st.error(f"**REKOMENDASI: {result['signal']} / Ambil Profit**")
            st.write("Pertimbangkan short atau tunggu di support.")

        else:
            st.warning("**HOLD** — Tunggu signal lebih jelas.")

        st.caption("Bukan saran finansial • Gunakan money management • Dibuat dengan Streamlit + CoinGecko")

st.markdown("---")
st.caption("Crypto TA Pro v2025 ")
