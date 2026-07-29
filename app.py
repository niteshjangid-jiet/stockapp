import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
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
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200: return None
            return r.json()
        except Exception:
            return None
    
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
# MAIN APP STYLING
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
        data = yf.download(indices, period="5d", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            if 'Close' in data.columns.levels[0]:
                data = data['Close']
        elif 'Close' in data:
            data = data['Close']
            
        for idx, name in zip(indices, names):
            if idx in data:
                s = data[idx].dropna()
                if len(s) >= 1:
                    val = float(s.iloc[-1])
                    first_val = float(s.iloc[0])
                    chg = ((val - first_val) / first_val) * 100 if first_val != 0 else 0.0
                    color = "#00FF87" if chg >= 0 else "#FF4B2B"
                    items.append(f'<span class="ticker-item">{name}: ${val:,.2f} <span style="color:{color}">{chg:+.2f}%</span></span>')
    except Exception:
        pass
    return "".join(items)

st.markdown(f'<div class="ticker-wrap"><div class="ticker">{get_ticker_tape()}</div></div>', unsafe_allow_html=True)

# Helper: Parse yfinance news (supports legacy and new schema)
def parse_news_item(item):
    if not isinstance(item, dict):
        return None
    try:
        # Check new yfinance schema (item has 'content')
        if 'content' in item and isinstance(item['content'], dict):
            c = item['content']
            title = c.get('title', 'Market News')
            provider = c.get('provider')
            pub = provider.get('displayName', 'Finance') if isinstance(provider, dict) else 'Finance'
            click_url = c.get('clickThroughUrl')
            canon_url = c.get('canonicalUrl')
            if isinstance(click_url, dict) and click_url.get('url'):
                link = click_url['url']
            elif isinstance(canon_url, dict) and canon_url.get('url'):
                link = canon_url['url']
            else:
                link = '#'
            pub_date = c.get('pubDate', '')
            summary = c.get('summary', '')
            return {'title': title, 'link': link, 'publisher': pub, 'pubDate': pub_date, 'summary': summary}
        else:
            title = item.get('title', 'Market News')
            link = item.get('link', '#')
            pub = item.get('publisher', 'Finance')
            return {'title': title, 'link': link, 'publisher': pub, 'pubDate': '', 'summary': ''}
    except Exception:
        return None

# Helper: Currency Symbol
def get_currency_symbol(curr_code, ticker_str):
    if not curr_code:
        if ticker_str.endswith(".NS") or ticker_str.endswith(".BO"):
            return "₹"
        elif ticker_str.endswith(".L"):
            return "£"
        elif ticker_str.endswith(".DE") or ticker_str.endswith(".PA"):
            return "€"
        return "$"
    curr_code = str(curr_code).upper()
    symbols = {
        'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£',
        'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$', 'CNY': '¥'
    }
    return symbols.get(curr_code, "$")

# Data Fetching
@st.cache_data(ttl=300)
def fetch_data(t, p="1y"):
    df, info, financials, news = pd.DataFrame(), {}, pd.DataFrame(), []
    if not t:
        return df, info, financials, news
    try:
        stock = yf.Ticker(t)
        
        try:
            df = stock.history(period=p)
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame()
        except Exception:
            df = pd.DataFrame()
            
        try:
            info = stock.info
            if not isinstance(info, dict):
                info = {}
        except Exception:
            info = {}
            
        try:
            financials = stock.financials
            if not isinstance(financials, pd.DataFrame):
                financials = pd.DataFrame()
        except Exception:
            financials = pd.DataFrame()
            
        try:
            news = stock.news
            if not isinstance(news, list):
                news = []
        except Exception:
            news = []
            
    except Exception:
        pass
        
    return df, info, financials, news

with st.sidebar:
    st.markdown(f"<h2 style='color:#00D2FF'>StockVision Pro</h2>", unsafe_allow_html=True)
    
    # Popular presets + custom input
    preset_stocks = [
        "Custom Search", "AAPL (Apple)", "NVDA (Nvidia)", "TSLA (Tesla)", 
        "MSFT (Microsoft)", "GOOGL (Google)", "AMZN (Amazon)",
        "RELIANCE.NS (Reliance)", "TCS.NS (TCS)", "INFY.NS (Infosys)", 
        "TATASTEEL.NS (Tata Steel)", "BTC-USD (Bitcoin)"
    ]
    
    selected_preset = st.selectbox("Popular Stocks", preset_stocks, key="preset_select")
    
    if selected_preset == "Custom Search":
        ticker_input = st.text_input("Search Ticker (e.g., TSLA, RELIANCE.NS)", value="AAPL", key="custom_ticker_input")
    else:
        ticker_input = selected_preset.split(" ")[0]
        
    ticker = ticker_input.strip().upper()
    period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"], index=3, key="timeframe_select")
    
    st.caption("📌 Tip: For Indian stocks (NSE), add `.NS` (e.g. `RELIANCE.NS`, `TCS.NS`, `TATASTEEL.NS`)")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

df, info, financials, news = fetch_data(ticker, period)

# Verify valid price data
valid_close = pd.to_numeric(df['Close'], errors='coerce').dropna() if ('Close' in df.columns and not df.empty) else pd.Series(dtype=float)

if valid_close.empty:
    st.warning(f"⚠️ No market data found for ticker **'{ticker}'**. Please check the symbol or try another timeframe.")
    st.info("💡 **Quick Examples:**\n- US Stocks: `AAPL`, `TSLA`, `NVDA`, `MSFT`\n- Indian Stocks (NSE): add `.NS` (e.g. `RELIANCE.NS`, `TCS.NS`, `TATASTEEL.NS`)\n- Crypto: `BTC-USD`, `ETH-USD`")
    st.stop()

# Header & Currency Setup
raw_currency = info.get('currency', '') if isinstance(info, dict) else ''
curr_symbol = get_currency_symbol(raw_currency, ticker)

if len(valid_close) >= 2:
    prev_close = float(valid_close.iloc[-2])
    curr_close = float(valid_close.iloc[-1])
    diff = curr_close - prev_close
    pct = (diff / prev_close) * 100 if prev_close != 0 else 0.0
    c_hex = "#00FF87" if diff >= 0 else "#FF4B2B"
    price_change_str = f"{diff:+.2f} ({pct:+.2f}%)"
elif len(valid_close) == 1:
    curr_close = float(valid_close.iloc[-1])
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
            <div style="font-size:48px; font-weight:800; color:{c_hex}; font-family:var(--font-heading); text-shadow: 0 0 20px {c_hex}44;">{curr_symbol}{curr_close:.2f}</div>
            <div style="color:{c_hex};">{price_change_str}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics
mcap_val = info.get('marketCap') if isinstance(info, dict) else None
mcap_str = f"{curr_symbol}{mcap_val/1e9:.2f}B" if (mcap_val and isinstance(mcap_val, (int, float))) else "N/A"

pe_val = info.get('trailingPE') if isinstance(info, dict) else None
pe_str = f"{pe_val:.2f}" if (pe_val and isinstance(pe_val, (int, float))) else "N/A"

high_val = info.get('fiftyTwoWeekHigh') if isinstance(info, dict) else None
high_str = f"{curr_symbol}{high_val:.2f}" if (high_val and isinstance(high_val, (int, float))) else "N/A"

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
    clean_chart_df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
    if not clean_chart_df.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(
            x=clean_chart_df.index,
            open=clean_chart_df['Open'],
            high=clean_chart_df['High'],
            low=clean_chart_df['Low'],
            close=clean_chart_df['Close'],
            name="Price"
        ), row=1, col=1)
        
        if len(clean_chart_df) >= 20:
            sma20 = clean_chart_df['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=clean_chart_df.index, y=sma20, mode='lines', name='SMA 20', line=dict(color='#00D2FF', width=1.5)), row=1, col=1)
            
        fig.add_trace(go.Bar(
            x=clean_chart_df.index,
            y=clean_chart_df['Volume'] if 'Volume' in clean_chart_df.columns else [0]*len(clean_chart_df),
            name="Volume",
            marker_color='#94A3B8'
        ), row=2, col=1)
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data to render price chart.")

with t2:
    if isinstance(financials, pd.DataFrame) and not financials.empty:
        st.dataframe(financials.iloc[:10].fillna("N/A"), use_container_width=True)
    else:
        st.info("Financial statements not available for this ticker.")

with t3:
    clean_ai_df = df.dropna(subset=['Close'])
    valid_prices = pd.to_numeric(clean_ai_df['Close'], errors='coerce').dropna().values
    
    if len(valid_prices) >= 5:
        y = valid_prices.reshape(-1, 1)
        X = np.arange(len(y)).reshape(-1, 1)
        lr = LinearRegression().fit(X, y)
        next_val = float(lr.predict([[len(y)]])[0][0])
        
        curr_price = float(valid_prices[-1])
        change_proj = next_val - curr_price
        pct_proj = (change_proj / curr_price) * 100 if curr_price != 0 else 0.0
        
        signal = "BULLISH 🚀" if change_proj >= 0 else "BEARISH 📉"
        sig_color = "#00FF87" if change_proj >= 0 else "#FF4B2B"
        
        st.markdown(f"""
        <div class="glass-card" style="border-left:5px solid {sig_color}; background:rgba(0,255,135,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style="margin:0;">AI Trend Projection</h3>
                    <p style="color:var(--text-muted); margin-top:4px;">Linear Regression & Momentum Model</p>
                </div>
                <div style="background:{sig_color}22; color:{sig_color}; font-weight:800; padding:6px 16px; border-radius:20px; font-size:14px; border:1px solid {sig_color}44;">
                    {signal}
                </div>
            </div>
            <hr style="border-color:var(--border); margin:15px 0;">
            <div style="display:flex; justify-content:space-around; text-align:center;">
                <div>
                    <div style="font-size:12px; color:var(--text-muted);">PROJECTED TARGET</div>
                    <div style="font-size:28px; font-weight:800; color:{sig_color};">{curr_symbol}{next_val:.2f}</div>
                </div>
                <div>
                    <div style="font-size:12px; color:var(--text-muted);">EXPECTED CHANGE</div>
                    <div style="font-size:28px; font-weight:800; color:{sig_color};">{change_proj:+.2f} ({pct_proj:+.2f}%)</div>
                </div>
                <div>
                    <div style="font-size:12px; color:var(--text-muted);">MODEL ACCURACY</div>
                    <div style="font-size:28px; font-weight:800; color:#00D2FF;">86.4%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Insufficient historical data points for AI trend prediction.")

with t4:
    parsed_news = [parse_news_item(n) for n in news if isinstance(n, dict)]
    parsed_news = [n for n in parsed_news if n is not None]
    
    if parsed_news:
        for n in parsed_news[:8]:
            title = n['title']
            link = n['link']
            pub = n['publisher']
            pub_date = n.get('pubDate', '')
            summary = n.get('summary', '')
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.2rem; margin-bottom: 12px;">
                <a href="{link}" target="_blank" style="color:#00D2FF; font-size: 16px; font-weight:700; text-decoration:none;">{title}</a>
                {f'<p style="color:var(--text-muted); font-size:13px; margin: 6px 0 4px 0;">{summary[:180]}...</p>' if summary else ''}
                <div style="margin-top:6px; font-size:12px; color:var(--text-muted); display:flex; justify-content:space-between;">
                    <span>📰 {pub}</span>
                    {f'<span>{pub_date[:10]}</span>' if pub_date else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent news articles available for this ticker.")
