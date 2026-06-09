# 📈 TML Analytics: IBD Daily Brief

TML Analytics is an institutional-grade, real-time momentum trading dashboard. Built on top of the Kush Tracker database, this application filters for True Market Leaders (TMLs) and applies real-time technical analysis (Minervini Trend Templates, VCP contraction detection) combined with 120B parameter AI synthesis to generate an actionable, "Bloomberg Terminal" style daily brief.

## ✨ Features
- **Real-Time Technical Engine:** Calculates Minervini Trend Templates (8 criteria), Volume Dry-Up, and Price Contractions (VCP) using live `yfinance` data.
- **120B AI Synthesis:** Leverages OpenRouter AI models to analyze Google News catalysts and technical setups, providing fundamental, technical, and momentum outlooks.
- **Extreme Futuristic UI:** Built with Streamlit, featuring an institutional-grade Cyberpunk design, dynamic live-pulsing SVG sparklines, glowing glassmorphic panels, and neon data-pills.
- **Filter for Action:** "Show 'Ready' Stocks Only" toggle instantly filters out developing setups to save API tokens and focus entirely on immediate breakout targets.

## 📂 Project Structure
- `app.py`: The main Streamlit dashboard and UI rendering engine.
- `data_engine.py`: Connects to the local `Kush Tracker` SQLite database to fetch the top 20 highest-scoring TML stocks.
- `technical_engine.py`: Connects to `yfinance` to evaluate Minervini trend conditions and VCP price/volume signatures.
- `analyst_engine.py`: Fetches recent fundamental news via RSS and generates the AI analyst brief using the OpenRouter API.
- `run.bat`: A quick-launch batch script for Windows users to start the app instantly.

## ⚙️ Prerequisites
- Python 3.9+
- A valid OpenRouter API Key for the AI Synthesis engine.
- The `Kush Tracker` project (with populated `kush_tracker.db`) located at `C:\projects\Kush Tracker\`.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "TML Analytics"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   ```

## 💻 Running the Application
You can launch the application directly by running the provided batch script:
```bash
./run.bat
```
Alternatively, start the Streamlit server manually:
```bash
streamlit run app.py
```

## ⚠️ Disclaimer
This software is for informational and educational purposes only. The AI synthesis and technical flags generated do not constitute financial advice. Always perform your own due diligence before executing trades.
