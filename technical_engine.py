import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def check_minervini_trend_template(df: pd.DataFrame) -> dict:
    """
    Check Minervini's Trend Template criteria.
    Requires df with 'close', 'high', 'low'.
    """
    result = {'passed': False, 'pass_count': 0, 'conditions': {}}
    if df.empty or len(df) < 200:
        return result

    last = df.iloc[-1]
    close = last['close']
    
    sma_150 = df['close'].rolling(window=150, min_periods=150).mean()
    sma_200 = df['close'].rolling(window=200, min_periods=200).mean()
    sma_50 = df['close'].rolling(window=50, min_periods=50).mean()

    if pd.isna(sma_150.iloc[-1]) or pd.isna(sma_200.iloc[-1]) or pd.isna(sma_50.iloc[-1]):
        return result

    sma_150_val = sma_150.iloc[-1]
    sma_200_val = sma_200.iloc[-1]
    sma_50_val = sma_50.iloc[-1]

    high_52w = df['high'].tail(252).max()
    low_52w = df['low'].tail(252).min()

    c1 = close > sma_150_val
    c2 = close > sma_200_val
    c3 = sma_150_val > sma_200_val
    c4 = len(sma_200) >= 22 and sma_200.iloc[-1] > sma_200.iloc[-22]
    c5 = sma_50_val > sma_150_val
    c6 = close > sma_50_val
    c7 = close >= high_52w * 0.75
    c8 = close >= low_52w * 1.30 if low_52w > 0 else False

    conditions = {
        'C1_Close_gt_150SMA': bool(c1),
        'C2_Close_gt_200SMA': bool(c2),
        'C3_150SMA_gt_200SMA': bool(c3),
        'C4_200SMA_Rising_1M': bool(c4),
        'C5_50SMA_gt_150SMA': bool(c5),
        'C6_Close_gt_50SMA': bool(c6),
        'C7_Within_25pct_52W_High': bool(c7),
        'C8_30pct_Above_52W_Low': bool(c8),
    }

    pass_count = sum(conditions.values())
    result['conditions'] = conditions
    result['pass_count'] = pass_count
    result['passed'] = pass_count >= 7
    return result

def detect_vcp_pattern(df: pd.DataFrame) -> dict:
    """
    Detect Volatility Contraction Pattern (VCP) over the last 10 weeks (50 days).
    """
    result = {'detected': False, 'num_contractions': 0, 'contractions': [], 'depth_shrinking': False}
    if df.empty or len(df) < 50:
        return result

    recent = df.tail(50)
    close = recent['close'].values
    high = recent['high'].values
    low = recent['low'].values

    segment_size = 5
    num_segments = len(close) // segment_size
    
    ranges = []
    for i in range(num_segments):
        start_idx = i * segment_size
        end_idx = start_idx + segment_size
        seg_high = high[start_idx:end_idx].max()
        seg_low = low[start_idx:end_idx].min()
        seg_mid = (seg_high + seg_low) / 2
        if seg_mid > 0:
            ranges.append(((seg_high - seg_low) / seg_mid) * 100)

    if len(ranges) < 4:
        return result

    contractions = []
    for i in range(1, len(ranges)):
        if ranges[i] < ranges[i - 1]:
            contraction_pct = (1 - ranges[i] / ranges[i - 1]) * 100
            contractions.append({
                'week': i + 1,
                'range_pct': ranges[i],
                'contraction_from_prior': contraction_pct,
            })

    significant = [c for c in contractions if c['contraction_from_prior'] >= 20]
    early_avg = np.mean(ranges[:3])
    late_avg = np.mean(ranges[-3:])
    depth_shrinking = late_avg < early_avg * 0.70

    result['contractions'] = contractions
    result['num_contractions'] = len(significant)
    result['depth_shrinking'] = depth_shrinking
    result['detected'] = len(significant) >= 2 and depth_shrinking
    return result

def check_volume_dryup(df: pd.DataFrame) -> bool:
    if df.empty or 'volume' not in df.columns or len(df) < 50:
        return False
    vol_5d = df['volume'].tail(5).mean()
    vol_50d = df['volume'].tail(50).mean()
    return vol_5d < (vol_50d * 0.50)

def calculate_buy_readiness(ticker: str, exchange_suffix: str = '.NS') -> dict:
    """
    Downloads historical data via yfinance and calculates technical state.
    """
    yf_ticker = f"{ticker}{exchange_suffix}"
    if exchange_suffix == '' and not ticker.startswith('^'): # US stocks usually have no suffix
        yf_ticker = ticker

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)
        stock = yf.Ticker(yf_ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty and exchange_suffix == '.NS': # fallback for BSE
            yf_ticker = f"{ticker}.BO"
            stock = yf.Ticker(yf_ticker)
            df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return {'score': 0, 'label': '⚪ Error', 'details': 'No data'}

        df.columns = df.columns.str.lower()
        
        # Calculate technicals
        minervini = check_minervini_trend_template(df)
        vcp = detect_vcp_pattern(df)
        vol_dryup = check_volume_dryup(df)
        
        close_price = df['close'].iloc[-1]
        high_52w = df['high'].tail(252).max()
        dist_from_high = ((high_52w - close_price) / high_52w) * 100 if high_52w > 0 else 100

        # Scoring
        score = 0
        if minervini['passed']: score += 3
        elif minervini['pass_count'] >= 6: score += 1
        
        if vcp['detected']: score += 2
        elif vcp['num_contractions'] >= 1 and vcp['depth_shrinking']: score += 1
        
        if vol_dryup: score += 1
        if dist_from_high <= 15: score += 1

        # Labels
        if score >= 5: label = '🟢 Ready'
        elif score >= 3: label = '🟡 Developing'
        else: label = '⚪ Not Ready'

        return {
            'ticker': ticker,
            'close': close_price,
            'dist_from_high': round(dist_from_high, 2),
            'minervini_passed': minervini['passed'],
            'minervini_count': minervini['pass_count'],
            'vcp_detected': vcp['detected'],
            'vcp_forming': vcp['num_contractions'] >= 1 and vcp['depth_shrinking'],
            'vol_dryup': vol_dryup,
            'score': score,
            'label': label
        }

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return {'score': 0, 'label': '⚪ Error', 'details': str(e)}
