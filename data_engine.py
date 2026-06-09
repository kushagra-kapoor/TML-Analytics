import sqlite3
import pandas as pd
import os
import json

LOCAL_DB_PATH = r"C:\projects\Kush Tracker\kush_tracker.db"
JSON_SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "tml_snapshot.json")

def get_db_connection(db_path: str = LOCAL_DB_PATH):
    return sqlite3.connect(db_path)

def get_latest_tml_snapshot(market: str = 'INDIA') -> list:
    """
    Returns the top 20 True Market Leaders for the selected market.
    Auto-detects Cloud vs Local environment.
    """
    if os.path.exists(LOCAL_DB_PATH):
        # Local Mode: Connect directly to the SQLite database
        return _fetch_from_db(market)
    else:
        # Cloud Mode: Fallback to the synced JSON snapshot
        return _fetch_from_json(market)

def _fetch_from_db(market: str) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the most recent date available for this market
        cursor.execute('''
            SELECT MAX(date) FROM tml_snapshot WHERE market = ?
        ''', (market,))
        
        latest_date_result = cursor.fetchone()
        if not latest_date_result or not latest_date_result[0]:
            return []
            
        latest_date = latest_date_result[0]
        
        cursor.execute('''
            SELECT ticker, rank, tml_score, industry, action_status 
            FROM tml_snapshot
            WHERE market = ? AND date = ?
            ORDER BY tml_score DESC, rank ASC
            LIMIT 20
        ''', (market, latest_date))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'ticker': row[0].replace('.NS', ''),
                'rank': row[1],
                'tml_score': row[2],
                'industry': row[3],
                'db_action': row[4]
            })
        return results
    except Exception as e:
        print(f"Error fetching TMLs from DB: {e}")
        return []
    finally:
        conn.close()

def _fetch_from_json(market: str) -> list:
    import streamlit as st
    try:
        if not os.path.exists(JSON_SNAPSHOT_PATH):
            st.error(f"Error: Neither DB nor JSON snapshot found at {JSON_SNAPSHOT_PATH}. Cannot load data.")
            return []
            
        with open(JSON_SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if market not in data:
            st.error(f"Error: Market {market} not found in JSON data keys: {list(data.keys())}")
            return []
            
        results = []
        for row in data[market]:
            results.append({
                'ticker': row['ticker'].replace('.NS', ''),
                'rank': row['rank'],
                'tml_score': row['tml_score'],
                'industry': row['industry'],
                'db_action': row['action_status']
            })
        return results
    except Exception as e:
        st.error(f"Exception fetching TMLs from JSON: {str(e)}")
        return []
