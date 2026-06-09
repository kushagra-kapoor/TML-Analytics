@echo off
echo ===================================================
echo Starting TML Analytics: IBD Daily Brief...
echo ===================================================
cd /d "%~dp0"
streamlit run app.py
pause
