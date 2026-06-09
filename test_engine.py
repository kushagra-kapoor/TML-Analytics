import sys
sys.path.append(r'C:\projects\TML Analytics')
from data_engine import get_latest_tml_snapshot
tmls = get_latest_tml_snapshot('INDIA')
print(f"Loaded {len(tmls)} items")
for tml in tmls:
    print(tml['rank'], type(tml['rank']), tml['ticker'])
