import streamlit as st
import time
import markdown
import os
from dotenv import load_dotenv

load_dotenv()

# Setup page config
st.set_page_config(page_title="TML Analytics", page_icon="⚡", layout="wide")

# --- SECURITY GATEWAY ---
def check_password():
    """Returns `True` if the user has the correct password."""
    # First check env (local .env or Streamlit Cloud env injection), fallback to st.secrets
    correct_password = os.getenv("APP_PASSWORD")
    if not correct_password:
        try:
            correct_password = st.secrets.get("APP_PASSWORD")
        except Exception:
            pass

    if correct_password:
        correct_password = str(correct_password).strip().strip('"').strip("'")

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Show input for password
    st.markdown("""
    <div style="text-align: center; margin-top: 100px;">
        <h1 style="margin: 0; font-size: 42px; font-weight: 900; letter-spacing: -2px; color: #fff; text-transform: uppercase; text-shadow: 0 0 20px rgba(0, 136, 255, 0.4);">
            <span style="color: #0088ff;">TML</span> Analytics
        </h1>
        <div style="color: #888; font-size: 12px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; margin-top: 5px; margin-bottom: 30px;">
            Restricted Institutional Terminal
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if not correct_password:
            st.error("⚠️ SYSTEM ERROR: The APP_PASSWORD secret is missing from Streamlit Cloud Secrets. Please add it via the 'Manage App' -> 'Settings' -> 'Secrets' menu.")
        else:
            password = st.text_input("Password", type="password", label_visibility="hidden", placeholder="Enter System Password...")
            if password:
                # Also strip user input just in case they added a space
                if password.strip() == correct_password:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("🔒 Access Denied: Incorrect Password")
    return False

if not check_password():
    st.stop()
# --- END SECURITY GATEWAY ---

from data_engine import get_latest_tml_snapshot
from technical_engine import calculate_buy_readiness
from analyst_engine import fetch_google_news_rss, generate_ibd_brief

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Force markdown lists inside our custom cards to be highly visible */
    .ibd-brief ul, .ibd-brief li, .ibd-brief p {
        color: rgba(255,255,255,0.8) !important;
        font-size: 14px !important;
        line-height: 1.8 !important;
    }
    .ibd-brief li {
        margin-bottom: 14px !important;
    }
    
    /* Hide the default Streamlit header link icon */
    a[href^="#"] {
        display: none !important;
    }
    
    /* Blinking / Pulsing animation for Ready stocks */
    @keyframes pulse-ready {
        0% { box-shadow: 0 0 0 0 rgba(0, 136, 255, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 136, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 136, 255, 0); }
    }
    .badge-ready {
        animation: pulse-ready 2s infinite;
        border: 1px solid #0088ff !important;
    }
    
    /* Institutional Pill Styling for LLM Bold text (e.g. **Technical edge:**) */
    .ibd-brief strong {
        color: #fff !important;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03)) !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-left: 2px solid #0088ff !important;
        margin-right: 6px !important;
        margin-left: 2px !important;
        display: inline-block !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.3) !important;
    }
    
    /* Hover effects for news items */
    .news-item {
        transition: all 0.3s ease;
    }
    .news-item:hover {
        color: #fff !important;
        transform: translateX(5px);
        text-shadow: 0 0 8px rgba(255,255,255,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Cyberpunk Header
st.markdown("""
<div style="padding: 25px 35px; background: linear-gradient(135deg, #0a0a0f 0%, #16161c 100%); border-radius: 12px; border-left: 4px solid #0088ff; border-top: 1px solid rgba(255,255,255,0.05); margin-bottom: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.02); border-right: 1px solid rgba(255,255,255,0.02);">
    <div>
        <h1 style="margin: 0; font-size: 42px; font-weight: 900; letter-spacing: -2px; color: #fff; text-transform: uppercase; text-shadow: 0 0 20px rgba(0, 136, 255, 0.4);">
            <span style="color: #0088ff;">TML</span> Analytics
        </h1>
        <div style="color: #888; font-size: 12px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; margin-top: 5px;">
            Institutional Momentum Engine <span style="color: #0088ff;">//</span> 120B AI Synthesis
        </div>
    </div>
    <div style="text-align: right; font-family: 'JetBrains Mono', monospace;">
        <div style="color: #00d26a; font-size: 14px; font-weight: 800; display: flex; align-items: center; justify-content: flex-end; gap: 10px; letter-spacing: 1px;">
            <div style="width: 8px; height: 8px; background: #00d26a; border-radius: 50%; box-shadow: 0 0 15px #00d26a; animation: pulse-ready 2s infinite;"></div>
            SYSTEM ONLINE
        </div>
        <div style="color: #555; font-size: 10px; margin-top: 6px; letter-spacing: 1px;">NODE: 0x4A9B | LATENCY: 12ms</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 Understanding the Scoring Engine (Methodology)"):
    st.markdown("""
    This dashboard calculates advanced technical patterns in real-time, completely independently from Kush Tracker. Here is how the scoring works:
    
    * **Minervini Trend Template (8/8):** Checks Mark Minervini's 8 strict criteria for a Stage 2 Uptrend. Includes rules like "Close > 150 SMA", "150 SMA > 200 SMA", and "Within 25% of 52-week High". A perfect score is 8/8. 6/8 or 7/8 implies a developing trend.
    * **VCP (Volatility Contraction Pattern):** Looks at the last 10 weeks of trading to find successive price contractions (e.g., 20% deep, then 10% deep, then 4% deep). *Yes* means the pattern is mathematically detected, indicating institutional absorption of supply.
    * **Volume Dry-Up:** Checks if the 5-day average volume has dropped below 50% of the 50-day average volume. This indicates selling pressure has exhausted itself, a prime setup for a breakout.
    
    **Buy Readiness Labels:**
    * 🟢 **Ready (Score 5+):** Stock passes Minervini, is tight, and shows VCP or volume dry-up. Ripe for a breakout.
    * 🟡 **Developing (Score 3-4):** Stock is in an uptrend but is still forming its base or hasn't tightened enough yet.
    * ⚪ **Not Ready (Score 0-2):** Trend is broken or the base is too deep/loose.
    """)

# Sidebar Controls
st.sidebar.header("Settings")
market_choice = st.sidebar.radio("Select Market:", ["INDIA", "US"])
show_ready_only = st.sidebar.checkbox("Show 'Ready' Stocks Only", value=False, help="Skip LLM analysis for stocks that do not have a Buy-Ready score (saves time & tokens).")

if st.sidebar.button("Generate Daily Brief", type="primary"):
    
    with st.spinner(f"Fetching Top 20 TMLs from {market_choice}..."):
        tmls = get_latest_tml_snapshot(market_choice)
    
    if not tmls:
        st.error("No True Market Leaders found. Please ensure Kush Tracker DB is populated.")
        st.stop()
        
    st.markdown(f"""
    <div style="background: rgba(0, 210, 106, 0.1); border: 1px solid rgba(0, 210, 106, 0.3); padding: 12px 20px; border-radius: 8px; margin-bottom: 25px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 16px;">✓</span>
        <span style="color: #00d26a; font-size: 13px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Sequence Initiated: {len(tmls)} True Market Leaders Loaded in Memory</span>
    </div>
    """, unsafe_allow_html=True)
    
    processed_count = 0
    skipped_count = 0
    
    # Progressive Rendering Loop
    for i, tml in enumerate(tmls):
        ticker = tml['ticker']
        rank = tml['rank']
        industry = tml['industry']
        
        # Create a container for this ticker so we can update it progressively
        container = st.empty()
        
        # Initial Loading State Card
        loading_html = f"""
<div style="background: #111115; padding: 25px; border-radius: 12px; border: 1px solid #222; margin-bottom: 20px;">
<h3 style="margin: 0; color: #888;">#{rank} {ticker} <span style="font-size: 14px; font-weight: normal; color: #555;">| {industry}</span></h3>
<p style="color: #666; font-size: 14px; margin-top: 10px;">⏳ Calculating VCP & fetching news...</p>
</div>
"""
        container.markdown(loading_html, unsafe_allow_html=True)
        
        # 1. Technical Engine (VCP / Minervini)
        suffix = '.NS' if market_choice == 'INDIA' else ''
        tech_data = calculate_buy_readiness(ticker, exchange_suffix=suffix)
        
        # Determine Color Based on Buy-Readiness Label
        label = tech_data.get('label', '⚪ Not Ready')
        is_ready = 'Ready' in label and 'Not' not in label
        
        # Apply Filter Logic
        if show_ready_only and not is_ready:
            container.empty() # Clear the loading card
            skipped_count += 1
            continue
            
        processed_count += 1
        
        # 2. News Engine
        news_items = fetch_google_news_rss(ticker)
        
        # Update Loading State to show LLM is thinking
        thinking_html = f"""
<div style="background: #111115; padding: 25px; border-radius: 12px; border: 1px solid #222; margin-bottom: 20px;">
<h3 style="margin: 0; color: #aaa;">#{rank} {ticker} <span style="font-size: 14px; font-weight: normal; color: #777;">| {industry}</span></h3>
<p style="color: #0088ff; font-size: 14px; margin-top: 10px;">🧠 Technicals calculated. Generating IBD Brief...</p>
</div>
"""
        container.markdown(thinking_html, unsafe_allow_html=True)
        
        # 3. LLM Synthesis
        brief_markdown = generate_ibd_brief(ticker, tech_data, news_items)
        
        if is_ready:
            border_color = "#00d26a" # Neon Green for Ready (more Deepvue style)
            bg_accent = "rgba(0, 210, 106, 0.15)"
            text_color = "#00d26a"
            badge_class = "badge-ready"
            label_text = f"🟢 {label}"
        elif 'Developing' in label:
            border_color = "#ffaa00" # Orange (Developing)
            bg_accent = "rgba(255, 170, 0, 0.15)"
            text_color = "#ffaa00"
            badge_class = ""
            label_text = f"🟡 {label}"
        else:
            border_color = "#ff007f" # Pink (Negative/Not Ready)
            bg_accent = "rgba(255, 0, 127, 0.15)"
            text_color = "#ff007f"
            badge_class = ""
            label_text = f"🔴 {label}"
            
        # Format the markdown to HTML for embedding
        brief_html = markdown.markdown(brief_markdown)
        
        # Format news items for display (removing the raw markdown dash since we handle HTML list manually)
        news_html_list = "".join([f"<li style='margin-bottom: 6px; line-height: 1.4;'>{item.replace('- **', '<strong>').replace('** <span', '</strong> <span')}</li>" for item in news_items])
        
        # Round the close price
        raw_close = tech_data.get('close', 'N/A')
        close_str = f"{raw_close:.2f}" if isinstance(raw_close, (int, float)) else str(raw_close)
        
        # Helper for color coding stats
        def get_stat_color(val):
            if val == 'Yes': return '#00d26a' # Neon green
            if val == 'No': return '#666' # Muted gray
            return '#eee'
            
        vcp_str = 'Yes' if tech_data.get('vcp_detected') else 'No'
        vol_str = 'Yes' if tech_data.get('vol_dryup') else 'No'
        
        dist_val = tech_data.get('dist_from_high', 100)
        dist_color = "#00d26a" if dist_val <= 5 else ("#ffaa00" if dist_val <= 15 else "#ff007f")
        
        miner_score = tech_data.get('minervini_count', 0)
        miner_color = "#00d26a" if miner_score >= 7 else ("#ffaa00" if miner_score >= 5 else "#ff007f")
        
        tv_exchange = "NSE:" if market_choice == 'INDIA' else ""
        tv_url = f"https://www.tradingview.com/chart/?symbol={tv_exchange}{ticker}"
        
        # Final Rendered Card (NO INDENTATION ALLOWED TO PREVENT MARKDOWN CODE BLOCKS)
        # Helper for Minervini Dots
        min_dots = ""
        for j in range(1, 9):
            dot_color = miner_color if j <= miner_score else "rgba(255,255,255,0.1)"
            min_dots += f'<div style="height: 4px; flex: 1; background: {dot_color}; border-radius: 2px;"></div>'
            
        # Helper for Distance Bar
        dist_pct = min(100, max(0, 100 - dist_val)) # How close to high
        
        # Helper for News cleanup in case backend didn't reload
        import re
        clean_news = []
        for item in news_items:
            # Strip ugly GMT dates if they slipped through
            item = re.sub(r' \([A-Z][a-z]{2}, \d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} GMT\)', '', item)
            clean_news.append(item)
            
        news_html_list = "".join([f"<li class='news-item' style='margin-bottom: 10px; line-height: 1.5;'>{item.replace('- **', '<strong>').replace('** <span', '</strong> <span')}</li>" for item in clean_news])
        
        # Helper: Generate 1-month SVG Sparkline dynamically
        try:
            import yfinance as yf
            hist_spark = yf.Ticker(ticker + suffix).history(period='1mo')['Close'].tolist()
            if hist_spark and len(hist_spark) > 1:
                min_p, max_p = min(hist_spark), max(hist_spark)
                rng = max_p - min_p if max_p != min_p else 1
                pts = []
                for idx, p in enumerate(hist_spark):
                    x = (idx / (len(hist_spark)-1)) * 100
                    y = 24 - ((p - min_p) / rng) * 24
                    pts.append(f"{x},{y}")
                spark_color = "#00d26a" if hist_spark[-1] >= hist_spark[0] else "#ff007f"
                spark_fill = f"rgba({0 if spark_color=='#00d26a' else 255}, {210 if spark_color=='#00d26a' else 0}, {106 if spark_color=='#00d26a' else 127}, 0.2)"
                # Add 0,24 and 100,24 to close the polygon for a beautiful gradient fill
                poly_pts = f"0,24 {' '.join(pts)} 100,24"
                
                # Extract last point for the pulsing node
                last_x, last_y = pts[-1].split(',')
                pulse_node = f'<circle cx="{last_x}" cy="{last_y}" r="2.5" fill="{spark_color}"><animate attributeName="r" values="2.5;6;2.5" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/></circle>'
                
                sparkline_html = f"""
<div style="margin-left: 20px; padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; justify-content: center;">
<div style="font-size: 8px; color: #666; text-transform: uppercase; margin-bottom: 2px; letter-spacing: 2px; font-weight: 800;">30D Trend</div>
<svg width="100" height="26" style="overflow: visible;">
<polygon fill="{spark_fill}" points="{poly_pts}"/>
<polyline fill="none" stroke="{spark_color}" stroke-width="2" points="{' '.join(pts)}" stroke-linecap="round" stroke-linejoin="round" filter="drop-shadow(0px 2px 4px {spark_color}80)"/>
{pulse_node}
</svg>
</div>
"""
            else:
                sparkline_html = ""
        except:
            sparkline_html = ""
        
        final_html = f"""
<div style="background-color: #0c0c0f; background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px); background-size: 20px 20px; padding: 30px; border-radius: 12px; border-left: 5px solid {border_color}; border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.02); border-bottom: 1px solid rgba(255,255,255,0.02); margin-bottom: 35px; font-family: 'JetBrains Mono', 'Inter', monospace, sans-serif; box-shadow: inset 0 0 50px rgba(0,0,0,0.5), 0 15px 35px rgba(0,0,0,0.6);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">
<div style="display: flex; align-items: center;">
<div>
<h3 style="margin: 0; font-size: 32px; font-weight: 900; letter-spacing: -1px; display: flex; align-items: center; gap: 12px; font-family: 'Inter', sans-serif;">
<span style="color: rgba(255,255,255,0.2); font-size: 20px; font-weight: 600;">#{rank}</span>
<a href="{tv_url}" target="_blank" style="color: #fff; text-decoration: none; transition: all 0.2s; text-shadow: 0 0 15px rgba(255,255,255,0.3);">{ticker} <span style="font-size: 16px; color: {border_color}; opacity: 0.8;">↗</span></a>
</h3>
<div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 800; margin-top: 4px; letter-spacing: 2px; text-transform: uppercase;">{industry}</div>
</div>
{sparkline_html}
</div>
<span class="{badge_class}" style="background: {bg_accent}; color: {text_color}; padding: 8px 18px; border-radius: 6px; font-size: 13px; font-weight: 800; text-transform: uppercase; border: 1px solid {border_color}; letter-spacing: 0.5px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); font-family: 'Inter', sans-serif;">{label_text}</span>
</div>
<div style="display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;">
<div style="background: rgba(255,255,255,0.02); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); min-width: 140px; flex: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2);">
<div style="color: rgba(255,255,255,0.4); font-size: 10px; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;">Close Price</div>
<div style="color: #fff; font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; text-shadow: 0 0 10px rgba(255,255,255,0.2);">{close_str}</div>
</div>
<div style="background: rgba(255,255,255,0.02); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); min-width: 140px; flex: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2);">
<div style="color: rgba(255,255,255,0.4); font-size: 10px; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;">From 52W High</div>
<div style="color: {dist_color}; font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; text-shadow: 0 0 10px {dist_color}40;">{dist_val}%</div>
<div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 8px; overflow: hidden; box-shadow: inset 0 0 3px rgba(0,0,0,0.5);">
<div style="width: {dist_pct}%; height: 100%; background: {dist_color}; box-shadow: 0 0 5px {dist_color};"></div>
</div>
</div>
<div style="background: rgba(255,255,255,0.02); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); min-width: 140px; flex: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2);">
<div style="color: rgba(255,255,255,0.4); font-size: 10px; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;">Minervini Trend</div>
<div style="color: {miner_color}; font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; text-shadow: 0 0 10px {miner_color}40;">{miner_score}<span style="color: rgba(255,255,255,0.2); font-size: 14px;">/8</span></div>
<div style="display: flex; gap: 3px; margin-top: 8px;">
{min_dots}
</div>
</div>
<div style="background: rgba(255,255,255,0.02); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); min-width: 140px; flex: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2);">
<div style="color: rgba(255,255,255,0.4); font-size: 10px; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;">VCP Detected</div>
<div style="color: {get_stat_color(vcp_str)}; font-size: 22px; font-weight: 700; text-shadow: 0 0 10px {get_stat_color(vcp_str)}40;">{vcp_str}</div>
</div>
<div style="background: rgba(255,255,255,0.02); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); min-width: 140px; flex: 1; box-shadow: inset 0 0 10px rgba(0,0,0,0.2);">
<div style="color: rgba(255,255,255,0.4); font-size: 10px; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; letter-spacing: 1px;">Volume Dry-Up</div>
<div style="color: {get_stat_color(vol_str)}; font-size: 22px; font-weight: 700; text-shadow: 0 0 10px {get_stat_color(vol_str)}40;">{vol_str}</div>
</div>
</div>
<div style="display: flex; gap: 30px;">
<div style="flex: 2; padding-right: 10px;">
<div style="color: #fff; font-size: 12px; text-transform: uppercase; font-weight: 800; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; letter-spacing: 2px; display: flex; align-items: center; gap: 8px;">
<span style="font-size: 16px; text-shadow: 0 0 10px rgba(255,255,255,0.5);">⚡</span> AI Synthesis
</div>
<div class="ibd-brief">
{brief_html}
</div>
</div>
<div style="flex: 1; background: rgba(255,255,255,0.01); border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); padding: 18px;">
<div style="color: rgba(255,255,255,0.6); font-size: 11px; text-transform: uppercase; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; letter-spacing: 1px;">
<span style="display: inline-block; width: 6px; height: 6px; background: {border_color}; border-radius: 50%; box-shadow: 0 0 8px {border_color};"></span>
Fundamental Catalysts
</div>
<ul style="color: #aaa; font-size: 13px; margin: 0; padding-left: 16px; list-style-type: circle;">
{news_html_list}
</ul>
</div>
</div>
</div>
"""
        container.markdown(final_html, unsafe_allow_html=True)
        
        # Small delay to prevent API throttling
        time.sleep(1)
        
    if show_ready_only:
        st.success(f"Daily Brief Complete. Analyzed {processed_count} Ready stocks. Skipped {skipped_count} non-Ready stocks.")
    else:
        st.success("Daily Brief Complete.")
