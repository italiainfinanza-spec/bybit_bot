import ccxt
import pandas as pd
from datetime import datetime, timedelta

exchange = ccxt.bybit({'enableRateLimit': True})

symbols = ["PIPPINUSDT","WIFUSDT","PEPEUSDT","BONKUSDT","FLOKIUSDT","POPCATUSDT","MOGUSDT","BRETTUSDT","DOGEUSDT","SHIBUSDT"]

def run_backtest():
    print("🔍 Backtest 180 giorni - strategia 500€ conservativa")
    for sym in symbols:
        try:
            since = int((datetime.now() - timedelta(days=180)).timestamp() * 1000)
            ohlcv = exchange.fetch_ohlcv(sym, timeframe='1h', since=since, limit=4000)
            df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
            df['pct24'] = df['close'].pct_change(24) * 100
            entries = df[df['pct24'] > 35].index.tolist()
            wins = 0
            for i in entries:
                entry_p = df.iloc[i]['close']
                future = df.iloc[i:i+96]['close']   # 4 giorni
                exit_p = future.min()
                pnl = (entry_p - exit_p) / entry_p * 100
                if pnl > 0: wins += 1
            winrate = (wins / len(entries) * 100) if entries else 0
            print(f"{sym:12} → {len(entries):2} segnali | Winrate {winrate:5.1f}%")
        except:
            print(f"{sym:12} → errore")
    print("Backtest finito!")

if __name__ == "__main__":
    run_backtest()
