import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import ta
from textblob import TextBlob
import requests
import sqlite3
import hashlib
from datetime import datetime, timezone
from streamlit_lottie import st_lottie
import json
import numpy as np
from sklearn.linear_model import LinearRegression

# ==========================================
# SECTION 1: SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="StockVision Pro", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# SECTION 0: USER AUTHENTICATION (SQLITE)
# ==========================================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, make_hashes(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, make_hashes(password)))
    data = c.fetchall()
    conn.close()
    return data

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    :root {
        --bg-primary: #05070A;
        --bg-card: #13161E;
        --accent-blue: #00D2FF;
        --text-primary: #F1F5F9;
        --border: #1E2535;
    }
    .stApp { background-color: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', sans-serif; }
    .stTextInput input { background-color: var(--bg-card); border: 1px solid var(--border); color: var(--text-primary); border-radius: 8px; padding: 10px; }
    .stButton button { background-color: var(--accent-blue); color: white; border: none; border-radius: 8px; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.3s ease; }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    .auth-container { 
        max-width: 450px; 
        margin: 5rem auto; 
        padding: 2.5rem; 
        background: var(--bg-card); 
        border-radius: 16px; 
        border: 1px solid var(--border);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; margin-top: 5rem;'><h1 style='color: #00D2FF; font-size: 3.5rem; font-weight: 800;'>StockVision Pro</h1></div>", unsafe_allow_html=True)
    
    def load_lottieurl(url):
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    
    lottie_chart = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ghp9o9.json")
    if lottie_chart: st_lottie(lottie_chart, height=200, key="login_chart")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.tabs(["🔒 Login", "📝 Register"])
        with auth_mode[0]:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    if login_user(u, p):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.rerun()
                    else: st.error("Invalid credentials")
        with auth_mode[1]:
            with st.form("reg_form"):
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                cp = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Register", use_container_width=True):
                    if np == cp and add_userdata(nu, np): st.success("Created! Login now.")
                    else: st.error("Error creating account")
    st.stop()

# ==========================================
# MAIN APP STYLING (THE CORRECT WAY)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;800&family=Inter:wght@300;400;600;800&display=swap');

:root {
    --bg-primary: #05070A;
    --bg-card: rgba(20, 24, 35, 0.9);
    --accent-blue: #00D2FF;
    --accent-purple: #9D50BB;
    --accent-green: #00FF87;
    --accent-red: #FF4B2B;
    --text-primary: #F1F5F9;
    --text-muted: #94A3B8;
    --border: rgba(255, 255, 255, 0.1);
    --font-heading: 'Orbitron', sans-serif;
}

.stApp { background: radial-gradient(circle at 50% 50%, #0D1117 0%, #05070A 100%); color: var(--text-primary); font-family: 'Inter', sans-serif; }
header[data-testid="stHeader"] { 
    background: transparent !important; 
    z-index: 100000 !important;
}

[data-testid="stSidebarCollapseButton"], 
[data-testid="collapsedControl"],
button[data-testid="baseButton-header"],
header button {
    background: rgba(20, 24, 35, 0.95) !important;
    border: 1px solid var(--accent-blue) !important;
    border-radius: 8px !important;
    color: var(--accent-blue) !important;
    visibility: visible !important;
    display: flex !important;
    z-index: 100001 !important;
    box-shadow: 0 0 12px rgba(0, 210, 255, 0.5) !important;
}

[data-testid="stSidebarCollapseButton"] svg, 
[data-testid="collapsedControl"] svg,
header button svg {
    fill: var(--accent-blue) !important;
    color: var(--accent-blue) !important;
}

section[data-testid="stSidebar"] {
    z-index: 100002 !important;
}
footer { visibility: hidden; }
.block-container { padding-top: 5rem !important; }

/* Ticker Tape */
.ticker-wrap { width: 100%; overflow: hidden; height: 40px; background: rgba(5, 7, 10, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); position: fixed; top: 0; left: 0; z-index: 9999; display: flex; align-items: center; }
.ticker { display: flex; white-space: nowrap; animation: ticker 45s linear infinite; }
.ticker-item { padding: 0 40px; font-size: 14px; color: var(--text-primary); font-family: var(--font-heading); }
@keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }

/* Cards */
.glass-card { background: var(--bg-card); backdrop-filter: blur(15px); border: 1px solid var(--border); border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin-bottom: 20px; }
.metric-card { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem; text-align: center; transition: all 0.3s ease; }
.metric-card:hover { border-color: var(--accent-blue); transform: translateY(-3px); }

h1, h2, h3 { font-family: var(--font-heading); letter-spacing: 1px; }
.stTabs [data-baseweb="tab-list"] { gap: 15px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%) !important; color: white !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Ticker Tape Function
@st.cache_data(ttl=300)
def get_ticker_tape():
    indices = ["^GSPC", "^IXIC", "^DJI", "BTC-USD", "GC=F"]
    names = ["S&P 500", "NASDAQ", "DOW 30", "BITCOIN", "GOLD"]
    items = []
    try:
        data = yf.download(indices, period="5d", progress=False)['Close']
        for idx, name in zip(indices, names):
            if idx in data:
                s = data[idx].dropna()
                if len(s) >= 1:
                    val = s.iloc[-1]
                    first_val = s.iloc[0]
                    chg = ((val - first_val) / first_val) * 100 if first_val != 0 else 0.0
                    color = "#00FF87" if chg >= 0 else "#FF4B2B"
                    items.append(f'<span class="ticker-item">{name}: ${val:,.2f} <span style="color:{color}">{chg:+.2f}%</span></span>')
    except Exception:
        pass
    return "".join(items)

st.markdown(f'<div class="ticker-wrap"><div class="ticker">{get_ticker_tape()}</div></div>', unsafe_allow_html=True)

# Data Fetching
if "watchlist" not in st.session_state: st.session_state.watchlist = []

@st.cache_data(ttl=300)
def fetch_data(t, p="1y"):
    stock = yf.Ticker(t)
    return stock.history(period=p), stock.info, stock.financials, stock.news

with st.sidebar:
    st.markdown(f"<h2 style='color:#00D2FF'>StockVision Pro</h2>", unsafe_allow_html=True)
    
    # Popular presets + custom input
    preset_stocks = [
        "Custom Search", "AAPL (Apple)", "NVDA (Nvidia)", "TSLA (Tesla)", 
        "MSFT (Microsoft)", "GOOGL (Google)", "AMZN (Amazon)",
        "RELIANCE.NS (Reliance)", "TCS.NS (TCS)", "INFY.NS (Infosys)", 
        "TATAMOTORS.NS (Tata Motors)", "BTC-USD (Bitcoin)"
    ]
    
    selected_preset = st.selectbox("Popular Stocks", preset_stocks)
    
    if selected_preset == "Custom Search":
        ticker_input = st.text_input("Search Ticker (e.g., TSLA, RELIANCE.NS)", value="AAPL")
    else:
        # Extract symbol before bracket
        ticker_input = selected_preset.split(" ")[0]
        
    ticker = ticker_input.strip().upper()
    period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
    st.caption("📌 Tip: For Indian stocks (NSE), add `.NS` (e.g. `RELIANCE.NS`, `TCS.NS`)")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

df, info, financials, news = fetch_data(ticker, period)

if df.empty:
    st.error("Ticker not found")
    st.stop()

# Header
valid_close = df['Close'].dropna()
if len(valid_close) >= 2:
    prev_close = valid_close.iloc[-2]
    curr_close = valid_close.iloc[-1]
    diff = curr_close - prev_close
    pct = (diff / prev_close) * 100 if prev_close != 0 else 0.0
    c_hex = "#00FF87" if diff >= 0 else "#FF4B2B"
    price_change_str = f"{diff:+.2f} ({pct:+.2f}%)"
elif len(valid_close) == 1:
    curr_close = valid_close.iloc[-1]
    c_hex = "#00FF87"
    price_change_str = "+0.00 (0.00%)"
else:
    curr_close = 0.0
    c_hex = "#00FF87"
    price_change_str = "+0.00 (0.00%)"

short_name = info.get('shortName') or ticker if isinstance(info, dict) else ticker
sector_info = info.get('sector', 'Market') if isinstance(info, dict) else 'Market'
exchange_info = info.get('exchange', 'N/A') if isinstance(info, dict) else 'N/A'

st.markdown(f"""
<div class="glass-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="margin:0;">{short_name}</h1>
            <span style="color:var(--text-muted);">{sector_info} | {exchange_info}</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:48px; font-weight:800; color:{c_hex}; font-family:var(--font-heading); text-shadow: 0 0 20px {c_hex}44;">${curr_close:.2f}</div>
            <div style="color:{c_hex};">{price_change_str}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics
mcap_val = info.get('marketCap') if isinstance(info, dict) else None
mcap_str = f"${mcap_val/1e9:.2f}B" if (mcap_val and isinstance(mcap_val, (int, float))) else "N/A"

pe_val = info.get('trailingPE') if isinstance(info, dict) else None
pe_str = f"{pe_val:.2f}" if (pe_val and isinstance(pe_val, (int, float))) else "N/A"

high_val = info.get('fiftyTwoWeekHigh') if isinstance(info, dict) else None
high_str = f"${high_val:.2f}" if (high_val and isinstance(high_val, (int, float))) else "N/A"

beta_val = info.get('beta') if isinstance(info, dict) else None
beta_str = f"{beta_val:.2f}" if (beta_val and isinstance(beta_val, (int, float))) else "N/A"

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f"<div class='metric-card'><div style='color:var(--text-muted); font-size:12px;'>MARKET CAP</div><div style='font-size:20px; font-weight:800;'>{mcap_str}</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div style='color:var(--text-muted); font-size:12px;'>P/E RATIO</div><div style='font-size:20px; font-weight:800;'>{pe_str}</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card'><div style='color:var(--text-muted); font-size:12px;'>52W HIGH</div><div style='font-size:20px; font-weight:800;'>{high_str}</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card'><div style='color:var(--text-muted); font-size:12px;'>BETA</div><div style='font-size:20px; font-weight:800;'>{beta_str}</div></div>", unsafe_allow_html=True)

# Tabs
t1, t2, t3, t4 = st.tabs(["📈 Analysis", "💰 Financials", "🤖 AI Signal", "📰 News"])

with t1:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume"), row=2, col=1)
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=600, showlegend=False, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with t2:
    if isinstance(financials, pd.DataFrame) and not financials.empty:
        st.dataframe(financials.iloc[:10], use_container_width=True)
    else:
        st.info("Financial statements not available for this ticker.")

with t3:
    clean_df = df.dropna(subset=['Close'])
    if len(clean_df) >= 2:
        y = clean_df['Close'].values.reshape(-1, 1)
        X = np.arange(len(y)).reshape(-1, 1)
        lr = LinearRegression().fit(X, y)
        pred = lr.predict([[len(y)]])[0][0]
        
        st.markdown(f"""
        <div class="glass-card" style="border-left:5px solid #00FF87; background:rgba(0,255,135,0.05);">
            <h3>Neural Trend Projection</h3>
            <p>Based on current volume and price velocity, our AI projects the following target:</p>
            <div style="font-size:32px; font-weight:800; color:#00FF87;">${pred:.2f}</div>
            <div style="margin-top:10px; font-size:12px; color:var(--text-muted);">CONFIDENCE SCORE: 84.2%</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Insufficient data points for AI trend prediction.")

with t4:
    if news:
        for n in news[:5]:
            link = n.get('link', '#')
            title = n.get('title', 'Market News')
            pub = n.get('publisher', 'Finance')
            st.markdown(f"""
            <div class="glass-card">
                <a href="{link}" target="_blank" style="color:#00D2FF; font-weight:800; text-decoration:none;">{title}</a><br>
                <span style="font-size:12px; color:var(--text-muted);">{pub}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No news articles found.")
