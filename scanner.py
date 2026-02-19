from bybit_client import get_tickers
from config import ENTRY_TRIGGER_PCT, MIN_TURNOVER_24H

def get_top_gainers():
    try:
        tickers = get_tickers()
    except Exception as e:
        print(f"⚠️  Errore get_tickers: {e}")
        return []
    gainers = []
    for t in tickers:
        try:
            pct = float(t["price24hPcnt"].replace("%",""))
            turnover = float(t["turnover24h"])
            symbol = t["symbol"]
            if pct >= ENTRY_TRIGGER_PCT and turnover > MIN_TURNOVER_24H and "USDT" in symbol:
                gainers.append({
                    "symbol": symbol,
                    "pct": pct,
                    "price": float(t["lastPrice"])
                })
        except: pass
    return sorted(gainers, key=lambda x: x["pct"], reverse=True)
