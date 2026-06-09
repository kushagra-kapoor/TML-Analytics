import sqlite3
import pandas as pd

def get_db_connection(db_path: str = r"C:\projects\Kush Tracker\kush_tracker.db"):
    return sqlite3.connect(db_path)

def get_latest_tml_snapshot(market: str = 'INDIA') -> list:
    """
    Returns the top 20 True Market Leaders for the selected market.
    """
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
        print(f"Error fetching TMLs: {e}")
        return []
    finally:
        conn.close()
