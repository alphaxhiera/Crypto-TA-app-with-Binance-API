# app.py — Crypto TA Pro v2025 + Stochastic + Penjelasan Lengkap
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Crypto TA Pro 2025", page_icon="Chart", layout="wide")

# ===================== FETCH DATA (PAKAI MARKET_CHART — ANTI-ERROR) =====================
@st.cache_data(ttl=600, show_spinner="Mengambil data dari CoinGecko...")
def get_price_data(coin_id: str, days: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        prices = r.json()["prices"]
        if len(prices) == 0:
            return None
        df = pd.DataFrame(prices, columns=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = df["close"].shift(1)
        df["high"] = df[["open", "close"]].max(axis=1)
        df["low"] = df[["open", "close"]].min(axis=1)
        df.loc[0, "open"] = df.loc[0, "close"]
        return df[["timestamp", "open", "high", "low", "close"]].reset_index(drop=True)
    except:
        return None

# ===================== SEMUA INDIKATOR =====================
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

# ===================== ANALISIS + PENJELASAN OTOMATIS =====================
def generate_full_analysis(df, coin_name):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest["close"]

    # === DETEKSI SIGNAL ===
    golden_cross = latest["sma_50"] > latest["sma_200"] and prev["sma_50"] <= prev["sma_200"]
    death_cross  = latest["sma_50"] < latest["sma_200"] and prev["sma_50"] >= prev["sma_200"]
    macd_bull = latest["macd"] > latest["macd_signal"] and prev["macd"] <= prev["macd_signal"]
    macd_bear = latest["macd"] < latest["macd_signal"] and prev["macd"] >= prev["macd_signal"]
    rsi_val = latest["rsi"]
    k = latest["%K"]
    d = latest["%D"]

    score = 0
    explanations = []

    # SMA
    if price > latest["sma_20"] > latest["sma_50"]:
        score += 2
        explanations.append("Harga di atas SMA 20 & 50 → Tren naik kuat")
    if golden_cross:
        score += 4
        explanations.append("Golden Cross (50/200) → Sinyal BULLISH kuat jangka panjang")
    if death_cross:
        score -= 4
        explanations.append("Death Cross (50/200) → Sinyal BEARISH kuat")

    # RSI
    if rsi_val < 30:
        score += 3
        explanations.append(f"RSI Oversold ({rsi_val:.1f}) → Kemungkinan rebound")
    elif rsi_val > 70:
        score -= 2
        explanations.append(f"RSI Overbought ({rsi_val:.1f}) → Risiko koreksi")

    # MACD
    if macd_bull:
        score += 2
        explanations.append("MACD Bullish Crossover → Momentum naik")
    if macd_bear:
        score -= 2
        explanations.append("MACD Bearish Crossover → Momentum turun")

    # Bollinger Bands
    if price < latest["bb_lower"]:
        score += 2
        explanations.append("Harga sentuh Lower Bollinger → Potensi bounce")
    if price > latest["bb_upper"]:
        score -= 2
        explanations.append("Harga sentuh Upper Bollinger → Potensi pullback")

    # Stochastic
    if k < 20 and d < 20 and k > d:
        score += 3
        explanations.append(f"Stochastic Oversold (%K={k:.1f}, %D={d:.1f}) + Bullish Cross → Reversal naik")
    if k > 80 and d > 80 and k < d:
        score -= 2
        explanations.append(f"Stochastic Overbought (%K={k:.1f}, %D={d:.1f}) + Bearish Cross → Reversal turun")

    # Final Signal
    if score >= 8:   signal, color = "STRONG BUY", "success"
    elif score >= 5: signal, color = "BUY", "success"
    elif score >= 1: signal, color = "WEAK BUY / HOLD", "warning"
    elif score >= -3: signal, color = "HOLD", "warning"
    elif score >= -6: signal, color = "SELL", "inverse"
    else:            signal, color = "STRONG SELL", "inverse"

    # Take Profit & Stop Loss
    resistance = df["high"].tail(90).max()
    support = df["low"].tail(90).min()
    tp1 = round(price * 1.06, 2)
    tp2 = round(price * 1.12, 2)
    tp3 = round(price * 1.25, 2)
    sl  = round(price * 0.92, 2)

    return {
        "signal": signal, "color": color, "score": score,
        "explanations": explanations, "price": price,
        "rsi": rsi_val, "k": k, "d": d,
        "tp1": tp1, "tp2": tp2, "tp3": tp3, "sl": sl,
        "support": support, "resistance": resistance,
        "golden_cross": golden_cross, "death_cross": death_cross
    }

# ===================== UI =====================
st.title("Crypto TA Pro 2025 + Stochastic")
st.markdown("**Signal Otomatis + Penjelasan Lengkap Setiap Indikator**")

with st.sidebar:
    st.header("Pilih Koin & Periode")
    coins = {
        "Bitcoin": "bitcoin", "Ethereum": "ethereum", "BNB": "binancecoin",
        "Solana": "solana", "XRP": "ripple", "Cardano": "cardano",
        "Dogecoin": "dogecoin", "Shiba Inu": "shiba-inu", "Pepe": "pepe",
        "Avalanche": "avalanche-2", "Toncoin": "toncoin"
    }
    coin_name = st.selectbox("Koin", options=list(coins.keys()))
    coin_id = coins[coin_name]
    period = st.selectbox("Periode", ["90", "180", "365", "max"], index=1)

if st.button("Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data & menghitung indikator..."):
        df_raw = get_price_data(coin_id, period)
        if df_raw is None or df_raw.empty:
            st.error("Gagal mengambil data. Coba koin lain.")
            st.stop()

        df = add_all_indicators(df_raw)
        df_valid = df.dropna()
        if df_valid.empty:
            df_valid = df.tail(150)

        result = generate_full_analysis(df_valid, coin_name)
        price = result["price"]

        # Dashboard Utama
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("Harga", f"${price:,.2f}")
        with c2: st.metric("RSI", f"{result['rsi']:.1f}")
        with c3: st.metric("Stoch %K", f"{result['k']:.1f}")
        with c4: st.metric("Trend", "Bull" if price > df_valid["sma_20"].iloc[-1] else "Bear")
        with c5:
            st.markdown(f"### **{result['signal']}**")
            st.caption(f"Score: {result['score']}/15")

        # Penjelasan Indikator
        st.success("Penjelasan Otomatis dari Indikator")
        for exp in result["explanations"]:
            st.write("Check: " + exp)

        # Chart Lengkap (5 panel)
        fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                            subplot_titles=("Candlestick + SMA + Bollinger", "RSI", "MACD", "Stochastic Oscillator", "Volume Proxy"),
                            row_heights=[0.45, 0.15, 0.15, 0.15, 0.1])

        # 1. Price + SMA + BB
        fig.add_trace(go.Candlestick(x=df_valid['timestamp'], open=df_valid['open'], high=df_valid['high'],
                                     low=df_valid['low'], close=df_valid['close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_20'], name="SMA 20", line=dict(color="orange")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['sma_50'], name="SMA 50", line=dict(color="blue")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['bb_upper'], name="BB Upper", line=dict(dash="dot", color="gray")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['bb_lower'], name="BB Lower", line=dict(dash="dot", color="gray")), row=1, col=1)

        # 2. RSI
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # 3. MACD
        colors = ['green' if v >= 0 else 'red' for v in df_valid['macd_hist']]
        fig.add_trace(go.Bar(x=df_valid['timestamp'], y=df_valid['macd_hist'], name="MACD Hist", marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_valid['timestamp'], y=df_valid['macd_signal'], name="Signal", line=dict(color="red")), row=3, col=1)

        # 4. Stochastic
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
            st.write(f"TP1 → `${result['tp1']}` (+6%)  \nTP2 → `${result['tp2']}` (+12%)  \nTP3 → `${result['tp3']}` (+25%)")
            st.write(f"**Stop Loss:** `${result['sl']}` (-8%)")
            st.write(f"Support: `${result['support']:.2f}` | Resistance: `${result['resistance']:.2f}`")
        else:
            st.warning(f"**{result['signal']}** — Tunggu atau ambil profit.")

        st.caption("Bukan saran investasi • DYOR • Dibuat dengan Streamlit + CoinGecko")

st.markdown("---")
st.caption("Crypto TA Gratis 100%")
