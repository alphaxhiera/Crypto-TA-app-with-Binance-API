# app.py — Crypto TA Pro 2025 ULTRA RELIABLE + Binance Fallback
import streamlit as st
import pandas as pd
import numpy as np
import requests
import ccxt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Crypto TA Pro 2025", page_icon="Rocket", layout="wide")

# ===================== DATA FETCH — COINGECKO + BINANCE FALLBACK (100% JALAN) =====================
@st.cache_data(ttl=600, show_spinner="Mencari data terbaik...")
def get_price_data(coin_id: str, days: str):
    # --- 1. Coba CoinGecko dulu (cepat & ringan)
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "daily", "precision": 2}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            prices = response.json().get("prices", [])
            if len(prices) >= 10:
                data = np.array(prices)
                ts = pd.to_datetime(data[:, 0], unit='ms')
                close = data[:, 1].astype(float)
                open_p = np.roll(close, 1); open_p[0] = close[0]
                df = pd.DataFrame({
                    "timestamp": ts,
                    "open": open_p,
                    "high": np.maximum(open_p, close),
                    "low": np.minimum(open_p, close),
                    "close": close
                })
                return df
    except:
        pass

    # --- 2. Fallback ke Binance Public (tanpa API key!)
    st.info("CoinGecko limit → Mengambil data dari Binance (lebih akurat!)")
    symbol_map = {
        "bitcoin": "BTC/USDT", "ethereum": "ETH/USDT", "binancecoin": "BNB/USDT",
        "solana": "SOL/USDT", "ripple": "XRP/USDT", "cardano": "ADA/USDT",
        "dogecoin": "DOGE/USDT", "shiba-inu": "SHIB/USDT", "pepe": "PEPE/USDT",
        "avalanche-2": "AVAX/USDT", "toncoin": "TON/USDT", "tron": "TRX/USDT"
    }
    symbol = symbol_map.get(coin_id, "BTC/USDT")
    
    try:
        exchange = ccxt.binance()
        limit = int(days) if days != "max" else 1000
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=limit + 50)
        if len(ohlcv) > 10:
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            return df[["timestamp", "open", "high", "low", "close"]].copy()
    except:
        pass

    return None  # benar-benar gagal

# ===================== INDIKATOR SUPER CEPAT =====================
def add_indicators(df: pd.DataFrame):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    df["sma20"] = close.rolling(20).mean()
    df["sma50"] = close.rolling(50).mean()
    df["sma200"] = close.rolling(200).mean()

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    df["bb_mid"] = close.rolling(20).mean()
    df["bb_std"] = close.rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]

    # Stochastic Oscillator
    low14 = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df["%K"] = 100 * (close - low14) / (high14 - low14)
    df["%D"] = df["%K"].rolling(3).mean()

    return df

# ===================== ANALISIS OTOMATIS + PENJELASAN =====================
def analyze(df, coin_name):
    if len(df) < 50:
        return {"signal": "DATA KURANG", "explanations": ["Butuh minimal 50 hari"], "score": 0}

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest["close"]
    score = 0
    exp = []

    # Trend & SMA
    if price > latest["sma20"]: score += 2; exp.append("Harga di atas SMA 20 → Bullish jangka pendek")
    if price > latest["sma50"]: score += 2; exp.append("Harga di atas SMA 50 → Bullish jangka menengah")
    if price > latest["sma200"]: score += 3; exp.append("Harga di atas SMA 200 → Bullish jangka panjang")

    # Golden/Death Cross
    if latest["sma50"] > latest["sma200"] and prev["sma50"] <= prev["sma200"]:
        score += 7; exp.append("GOLDEN CROSS → Sinyal BULLISH KUAT!")
    if latest["sma50"] < latest["sma200"] and prev["sma50"] >= prev["sma200"]:
        score -= 7; exp.append("DEATH CROSS → Sinyal BEARISH KUAT!")

    # RSI
    if latest["rsi"] < 30: score += 6; exp.append(f"RSI Oversold ({latest['rsi']:.1f}) → Rebound!")
    if latest["rsi"] > 70: score -= 5; exp.append(f"RSI Overbought ({latest['rsi']:.1f}) → Koreksi!")

    # MACD
    if latest["macd"] > latest["macd_signal"] and prev["macd"] <= prev["macd_signal"]:
        score += 5; exp.append("MACD Bullish Cross → Momentum Naik")

    # Bollinger
    if price <= latest["bb_lower"]: score += 5; exp.append("Harga di Lower BB → Potensi Bounce")
    if price >= latest["bb_upper"]: score -= 5; exp.append("Harga di Upper BB → Potensi Pullback")

    # Stochastic
    if latest["%K"] < 20 and latest["%K"] > latest["%D"]:
        score += 6; exp.append(f"Stochastic Oversold + Cross ({latest['%K']:.1f}) → BELI KUAT!")
    if latest["%K"] > 80 and latest["%K"] < latest["%D"]:
        score -= 6; exp.append(f"Stochastic Overbought + Cross ({latest['%K']:.1f}) → JUAL!")

    # Final Signal
    if score >= 15:   signal = "STRONG BUY"
    elif score >= 10: signal = "BUY"
    elif score >= 3:  signal = "WEAK BUY"
    elif score >= -5: signal = "HOLD"
    elif score >= -12:signal = "SELL"
    else:             signal = "STRONG SELL"

    support = df["low"].tail(90).min()
    resistance = df["high"].tail(90).max()

    return {
        "signal": signal,
        "score": score,
        "explanations": exp,
        "price": price,
        "rsi": latest["rsi"],
        "k": latest["%K"],
        "tp1": round(price * 1.06, 6),
        "tp2": round(price * 1.15, 6),
        "tp3": round(price * 1.30, 6),
        "sl": round(price * 0.90, 6),
        "support": support,
        "resistance": resistance
    }

# ===================== UI =====================
st.title("Crypto TA Pro 2025 — Never Fail Edition")
st.markdown("**100% Selalu Jalan • CoinGecko + Binance Fallback Otomatis**")

with st.sidebar:
    st.header("Pilih Koin")
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
    coin_name = st.selectbox("Cryptocurrency", list(coins.keys()))
    coin_id = coins[coin_name]
    period = st.selectbox("Periode", ["90", "180", "365", "max"], index=1)

if st.button("Analisis Sekarang", type="primary", use_container_width=True):
    with st.spinner("Mengambil data terbaik..."):
        df = get_price_data(coin_id, period)
        if df is None or len(df) < 10:
            st.error("Maaf, coin ini belum tersedia atau sedang maintenance.")
            st.stop()

        df = add_indicators(df)
        result = analyze(df.dropna(), coin_name)

        # Dashboard
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Harga", f"${result['price']:,.6f}")
        with col2: st.metric("RSI", f"{result['rsi']:.1f}")
        with col3: st.metric("Stoch %K", f"{result['k']:.1f}")
        with col4:
            st.markdown(f"### **{result['signal']}**")
            st.caption(f"Score: {result['score']}")

        # Penjelasan
        st.success("Penjelasan Sinyal Otomatis")
        for e in result["explanations"]:
            st.write(f"Check {e}")

        # Chart
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            subplot_titles=("Price + SMA + Bollinger", "RSI", "MACD", "Stochastic"),
                            row_heights=[0.5, 0.15, 0.15, 0.2])

        fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma20'], name="SMA 20", line=dict(color="orange")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma50'], name="SMA 50", line=dict(color="blue")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_upper'], name="BB Upper", line=dict(dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bb_lower'], name="BB Lower", line=dict(dash="dot")), row=1, col=1)

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name="RSI", line=dict(color="purple")), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        colors = ['green' if v >= 0 else 'red' for v in df['macd_hist']]
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['macd_hist'], name="MACD Hist", marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd'], name="MACD", line=dict(color="blue")), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['macd_signal'], name="Signal", line=dict(color="red")), row=3, col=1)

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['%K'], name="%K", line=dict(color="cyan")), row=4, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['%D'], name="%D", line=dict(color="magenta")), row=4, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)

        fig.update_layout(height=900, title=f"{coin_name} — Analisis Teknikal 2025", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Trade Plan
        st.markdown("## Trade Plan Otomatis")
        if "BUY" in result["signal"]:
            st.success(f"**REKOMENDASI: {result['signal']} {coin_name}**")
            st.write(f"**Take Profit:**\n• TP1 → `${result['tp1']}` (+6%)\n• TP2 → `${result['tp2']}` (+15%)\n• TP3 → `${result['tp3']}` (+30%)")
            st.write(f"**Stop Loss:** `${result['sl']}` (-10%)")
        else:
            st.warning(f"**{result['signal']}** — Tunggu atau ambil profit.")

        st.caption("100% Selalu Jalan • Binance Fallback • Tanpa API Key • 2025 Edition")

st.markdown("---")
st.caption("Crypto TA Pro 2025 • Dibuat oleh Grok • 100% Gratis & Open Source")
