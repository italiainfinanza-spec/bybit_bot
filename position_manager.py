from bybit_client import place_short_market, get_position, close_position, set_cross_margin, get_current_price
from config import INITIAL_MARGIN, DCA_MULTIPLIER, LEVERAGE, HARD_STOP_PCT, PROFIT_TARGET_PCT, MAX_DCA
from telegram_notifier import send_message, get_updates
import time

active_trades = {}   # symbol → dict
pending_signals = {} # symbol → {"price": float, "time": float}

CONFIRM_TIMEOUT = 300  # 5 minuti per confermare

def build_signal_message(symbol, price):
    qty = (INITIAL_MARGIN * LEVERAGE) / price
    target_price = price * (1 - PROFIT_TARGET_PCT / 100)
    stop_price   = price * (1 + HARD_STOP_PCT / 100)
    max_profit   = INITIAL_MARGIN * LEVERAGE * PROFIT_TARGET_PCT / 100
    max_loss     = INITIAL_MARGIN * LEVERAGE * HARD_STOP_PCT / 100

    dca_lines = []
    total_margin = INITIAL_MARGIN
    dca_trigger  = price
    for i in range(1, MAX_DCA + 1):
        dca_trigger  = dca_trigger * 1.08
        dca_margin   = INITIAL_MARGIN * (DCA_MULTIPLIER ** i)
        total_margin += dca_margin
        dca_lines.append(
            f"  #{i}  @ {dca_trigger:.4f}  (+{round(8*i)}%)  | +{dca_margin:.2f} USDT margin"
        )

    return (
        f"🔔 SEGNALE SHORT: {symbol}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Entry price:   {price:.4f} USDT\n"
        f"📦 Quantità:      {qty:.4f}\n"
        f"💰 Margin:        {INITIAL_MARGIN} USDT  |  Leva: {LEVERAGE}x\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Take Profit:   {target_price:.4f}  (-{PROFIT_TARGET_PCT}%)  → +{max_profit:.2f} USDT\n"
        f"🛑 Stop Loss:     {stop_price:.4f}  (+{HARD_STOP_PCT}%)   → -{max_loss:.2f} USDT\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"➕ DCA automatici (se il prezzo sale):\n"
        + "\n".join(dca_lines) + "\n"
        f"  Margin totale (tutti DCA): {total_margin:.2f} USDT\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Rispondi /ok_{symbol} per confermare (5 min)"
    )

def manage_trade(symbol, current_price):
    # Segnale già in attesa di conferma → ignora
    if symbol in pending_signals:
        return

    if symbol not in active_trades:
        # Nuovo segnale: chiedi conferma via Telegram
        pending_signals[symbol] = {"price": current_price, "time": time.time()}
        msg = build_signal_message(symbol, current_price)
        print(msg)
        send_message(msg)
        return

    trade = active_trades[symbol]
    unrealized_pct = (trade["avg_price"] - current_price) / trade["avg_price"] * 100

    # HARD STOP
    if unrealized_pct < -HARD_STOP_PCT:
        close_position(symbol)
        del active_trades[symbol]
        msg = f"HARD STOP {symbol} | PnL: {unrealized_pct:.2f}%"
        print(f"❌ {msg}")
        send_message(f"❌ {msg}")
        return

    # PROFIT TARGET
    if unrealized_pct > PROFIT_TARGET_PCT:
        close_position(symbol)
        del active_trades[symbol]
        msg = f"TARGET RAGGIUNTO {symbol} | PnL: +{unrealized_pct:.2f}%"
        print(f"🎉 {msg}")
        send_message(f"🎉 {msg}")
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
        msg = f"DCA #{trade['entries']} {symbol} @ {current_price} | Nuovo avg: {trade['avg_price']:.4f} | Margin totale: {trade['total_margin']:.2f} USDT"
        print(f"➕ {msg}")
        send_message(f"➕ {msg}")

def check_confirmations():
    now = time.time()

    # Scaduti: rimuovi e notifica
    expired = [s for s, v in list(pending_signals.items()) if now - v["time"] > CONFIRM_TIMEOUT]
    for s in expired:
        del pending_signals[s]
        print(f"⏰ Segnale scaduto: {s}")
        send_message(f"⏰ Segnale scaduto senza conferma: {s}")

    if not pending_signals:
        return

    # Leggi risposte Telegram
    for update in get_updates():
        text = update.get("message", {}).get("text", "")
        if not text.startswith("/ok_"):
            continue
        symbol = text[4:].upper().strip()
        if symbol not in pending_signals:
            continue

        del pending_signals[symbol]
        current_price = get_current_price(symbol)
        if not current_price:
            send_message(f"❌ Prezzo non disponibile per {symbol}, trade annullato")
            continue

        set_cross_margin(symbol)
        qty = (INITIAL_MARGIN * LEVERAGE) / current_price
        place_short_market(symbol, qty)
        active_trades[symbol] = {
            "avg_price": current_price,
            "total_margin": INITIAL_MARGIN,
            "entries": 1,
            "size": qty
        }
        msg = f"SHORT APERTO {symbol} @ {current_price} | Margin: {INITIAL_MARGIN} USDT | Qty: {qty:.4f}"
        print(f"✅ {msg}")
        send_message(f"✅ {msg}")
