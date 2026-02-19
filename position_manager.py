from bybit_client import place_short_market, get_position, close_position, set_cross_margin, get_current_price
from config import INITIAL_MARGIN, DCA_MULTIPLIER, LEVERAGE, HARD_STOP_PCT, PROFIT_TARGET_PCT, MAX_DCA
import time

active_trades = {}  # symbol → dict

def manage_trade(symbol, current_price):
    if symbol not in active_trades:
        # Prima entrata
        set_cross_margin(symbol)
        qty = (INITIAL_MARGIN * LEVERAGE) / current_price
        place_short_market(symbol, qty)
        active_trades[symbol] = {
            "avg_price": current_price,
            "total_margin": INITIAL_MARGIN,
            "entries": 1,
            "size": qty
        }
        print(f"✅ SHORT APERTO {symbol} @ {current_price}")
        return

    trade = active_trades[symbol]
    unrealized_pct = (trade["avg_price"] - current_price) / trade["avg_price"] * 100   # positivo = profitto per short

    # HARD STOP
    if unrealized_pct < -HARD_STOP_PCT:
        close_position(symbol)
        del active_trades[symbol]
        print(f"❌ HARD STOP {symbol}")
        return

    # PROFIT TARGET
    if unrealized_pct > PROFIT_TARGET_PCT:
        close_position(symbol)
        del active_trades[symbol]
        print(f"🎉 TARGET RAGGIUNTO {symbol}")
        return

    # DCA
    if trade["entries"] < MAX_DCA and current_price > trade["avg_price"] * 1.08:
        new_margin = INITIAL_MARGIN * (DCA_MULTIPLIER ** trade["entries"])
        qty = (new_margin * LEVERAGE) / current_price
        place_short_market(symbol, qty)
        trade["total_margin"] += new_margin
        trade["entries"] += 1
        trade["avg_price"] = (trade["avg_price"] * trade["size"] + current_price * qty) / (trade["size"] + qty)
        trade["size"] += qty
        print(f"➕ DCA #{trade['entries']} su {symbol}")
