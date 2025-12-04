# app.py — Crypto Technical Analysis Pro 2025 + Stochastic + Penjelasan Lengkap
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Crypto TA Pro 2025", page_icon="Chart", layout="wide")

# ===================== FETCH DATA (CoinGecko Market Chart — 100% Stabil) =====================
@st.cache_data(ttl=600, show_spinner="Mengambil data harga dari CoinGecko...")
def get_price_data(coin_id: str, days: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return None
        data = response.json().get("prices", [])
        if len(data) == 0:
            return None

        df = pd.DataFrame(data, columns=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = df["close"].shift(1)
        df["high"] = df[["open", "close"]].max(axis=1)
        df["low"] = df[["open", "close"]].min(axis=1)
        df.loc[0, "open"] = df.loc[0, "close"]
        return df[["timestamp", "open", "high", "low", "close"]].reset_index(drop=True)
    except:
        return None

# ===================== SEMUA INDIKATOR + STOCHASTIC =====================
def add_all_indicators(df: pd.DataFrame):
    df = df.copy()
    
    # SMA
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
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    df["bb_mid"] = df["close"].rolling(20).mean()
    df["bb_std"] = df["close"].rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + (df["bb_std"] * 2)
    df["bb_lower"] = df["bb_mid"] - (df["bb_std"] * 2)

    # Stochastic Oscillator (14,3,3)
    low_14 = df["low"].rolling(14).min()
    high_14 = df["high"].rolling(14).max()
    df["%K"] = 100 * (df["close"] - low_14) / (high_14 - low_14)
    df["%D"] = df["%K"].rolling(3).mean()

    return df

# ===================== ANALISIS + PENJELASAN OTOMATIS (FIXED!) =====================
def generate_analysis(df, coin_name):
    if len(df) < 50:
        return {"signal": "DATA KURANG", "explanations": ["Perlu minimal 50 hari data untuk analisis akurat"]}

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    price = latest["close"]

    score = 0
    explanations = []

    # SMA & Trend
    if price > latest["sma_20"]:
        score += 1
        explanations.append("Harga di atas SMA 20 → Tren naik jangka pendek")
    if price > latest["sma_50"]:
        score += 1
        explanations.append("Harga di atas SMA 50 → Tren naik jangka menengah")
    if price > latest["sma_200"]:
        score += 2
        explanations.append("Harga di atas SMA 200 → Tren BULLISH jangka panjang")

    # Golden / Death Cross
    golden_cross = latest["sma_50"] > latest["sma_200"] and prev["sma_50"] <= prev["sma_200"]
    death_cross = latest["sma_50"] < latest["sma_200"] and prev["sma_50"] >= prev["sma_200"]
    if golden_cross:
        score += 5
        explanations.append("GOLDEN CROSS TERJADI → Sinyal BULLISH sangat kuat!")
    if death_cross:
        score -= 5
        explanations.append("DEATH CROSS TERJADI → Sinyal BEARISH sangat kuat!")

    # RSI
    rsi_val = latest["rsi"]
    if rsi_val < 30:
        score += 4
        explanations.append(f"RSI Oversold ({rsi_val:.1f}) → Kemungkinan besar rebound!")
    elif rsi_val > 70:
        score -= 3
        explanations.append(f"RSI Overbought ({rsi_val:.1f}) → Rawan koreksi turun")

    # MACD
    macd_bull = latest["macd"] > latest["macd_signal"] and prev["macd"] <= prev["macd_signal"]
    macd_bear = latest["macd"] < latest["macd_signal"] and prev["macd"] >= prev["macd_signal"]
    if macd_bull:
        score += 3
        explanations.append("MACD Bullish Crossover → Momentum naik kuat")
    if macd_bear:
        score -= 3
        explanations.append("MACD Bearish Crossover → Momentum turun")

    # Bollinger Bands
    if price <= latest["bb_lower"] * 1.01:
        score += 3
        explanations.append("Harga menyentuh Lower Bollinger → Potensi bounce kuat")
    if price >= latest["bb_upper"] * 0.99:
        score -= 3
        explanations.append("Harga menyentuh Upper Bollinger → Potensi pullback")

    # Stochastic Oscillator
    k = latest["%K"]
    d = latest["%D"]
    if k < 20 and d < 20 and k > d:
        score += 4
        explanations.append(f"Stochastic Oversold + Bullish Cross (%K={k:.1f}) → Sinyal beli sangat kuat!")
    if k > 80 and d > 80 and k < d:
        score -= 4
        explanations.append(f"Stochastic Overbought + Bearish Cross (%K={k:.1f}) → Sinyal jual!")

    # Final Signal
    if score >= 10:
        signal = "STRONG BUY"
        color = "success"
    elif score >= 6:
        signal = "BUY"
        color = "success"
    elif score >= 2:
        signal = "WEAK BUY / HOLD"
        color = "warning"
    elif score >= -3:
        signal = "HOLD"
        color = "warning"
    elif score >= -8:
        signal = "SELL"
        color = "inverse"
    else:
        signal = "STRONG SELL"
        color = "inverse"

    # Take Profit & Stop Loss
    resistance = df["high"].tail(90).max()
    support = df["low"].tail(90).min()
    tp1 = round(price * 1.06, 2)
    tp2 = round(price * 1.15, 2)
    tp3 = round(price * 1.30, 2)
    sl = round(price * 0.90, 2)

    return {
        "signal": signal,
        "color": color,
        "score": score,
        "explanations": explanations,   # PASTI MUNCUL SEKARANG!
        "price": price,
        "rsi": rsi_val,
        "k": k,
        "d": d,
        "tp1": tp1, "tp2": tp2, "tp3": tp3, "sl": sl,
        "support": support, "resistance": resistance
    }

# ===================== UI =====================
st.title("Crypto TA Pro 2025 + Stochastic Oscillator")
st.markdown("**Signal Otomatis + Penjelasan Lengkap untuk Setiap Indikator**")

with st.sidebar:
    st.header("Pilih Koin & Periode")
    coins = {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "BNB": "binancecoin",
        "Solana": "solana",
        "XRP": "ripple",
        "Cardano": "cardano",
        "Dogecoin": "dogecoin",
        "Shiba Inu": "shiba-inu",
        "Pepe": "pepe",
        "Avalanche": "avalanche-2",
        "Toncoin": "toncoin",
        "TRON": "tron"
    }
    coin_name = st.selectbox("Cryptocurrency", options=list(coins.keys()), index=0)
    coin_id = coins[coin_name]
    period = st.selectbox("Periode Analisis", ["90", "180", "365", "max"], index=1)

if st.button("Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner(f"Menganalisis {coin_name}..."):
        df_raw = get_price_data(coin_id, period)
        if df_raw is None or df_raw.empty:
            st.error(f"Gagal mengambil data untuk {coin_name}. Coba koin lain.")
            st.stop()

        df = add_all_indicators(df_raw)
        df_valid = df.dropna()
        if df_valid.empty:
            df_valid = df.tail(200)

        result = generate_analysis(df_valid, coin_name)
        price = result["price"]

        # Dashboard
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("Harga Saat Ini", f"${price:,.2f}")
        with col2: st.metric("RSI (14)", f"{result['rsi']:.1f}")
        with col3: st.metric("Stoch %K", f"{result['k']:.1f}")
        with col4: st.metric("Skor Signal", f"{result['score']}/18")
        with col5:
            st.markdown(f"### **{result['signal']}**")
            st.caption("Berdasarkan 6 indikator teknikal")

        # PENJELASAN OTOMATIS — SEKARANG PASTI MUNCUL!
        st.success("Penjelasan Otomatis dari Semua Indikator")
        if result["explanations"]:
            for exp in result["explanations"]:
                st.write(f"Check {exp}")
        else:
            st.info("Tidak ada sinyal kuat saat ini → Market sideways atau ranging.")

        # Chart Lengkap
        fig = make_subplots(
            rows=5, cols=1, shared_xaxes=True,
            subplot_titles=("Price + SMA + Bollinger Bands", "RSI", "MACD", "Stochastic Oscillator", "Volume Proxy"),
            row_heights=[0.45, 0.15, 0.15, 0.15, 0.1]
        )

        # Candlestick + SMA + BB
        fig.add_trace(go.Candlestick(x=df_valid['timestamp'], open=df_valid['open'], high=df_valid['high'],
                                     low=df_valid['low'], close=df_valid['close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_20'], name="SMA 20", line=dict(color="#00ff00")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_50'], name="SMA 50", line=dict(color="#ffaa00")), row=1, col=1)
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
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['macd_signal'], name="Signal", line=dict(color="orange")), row=3, col=1)

        # Stochastic
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['%K'], name="%K", line=dict(color="cyan")), row=4, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['%D'], name="%D", line=dict(color="magenta")), row=4, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)

        fig.update_layout(height=1000, title=f"{coin_name} — Analisis Teknikal Lengkap 2025", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Trade Plan
        st.markdown("## Trade Plan Otomatis")
        if "BUY" in result["signal"]:
            st.success(f"**REKOMENDASI: {result['signal']} {coin_name}**")
            st.write(f"**Take Profit:**\n• TP1 → `${result['tp1']}` (+6%)\n• TP2 → `${result['tp2']}` (+15%)\n• TP3 → `${result['tp3']}` (+30%)")
            st.write(f"**Stop Loss:** `${result['sl']}` (-10%)")
            st.write(f"Support: `${result['support']:.2f}` | Resistance: `${result['resistance']:.2f}`")
        elif "SELL" in result["signal"]:
            st.error(f"**REKOMENDASI: {result['signal']} / Ambil Profit**")
        else:
            st.warning("**HOLD** — Tunggu sinyal lebih jelas.")

        st.caption("Bukan saran finansial • DYOR- Streamlit + CoinGecko")

st.markdown("---")
st.caption("Crypto TA Pro 2025")
