from pybit.unified_trading import HTTP
from config import API_KEY, API_SECRET, TESTNET, LEVERAGE

session = HTTP(testnet=TESTNET, api_key=API_KEY, api_secret=API_SECRET, recv_window=10000, timeout=10)

def set_cross_margin(symbol):
    try:
        session.set_margin_mode(category="linear", symbol=symbol, buyMarginMode="cross", sellMarginMode="cross")
        session.set_leverage(category="linear", symbol=symbol, buyLeverage=LEVERAGE, sellLeverage=LEVERAGE)
    except: pass

def get_tickers():
    return session.get_tickers(category="linear")["result"]["list"]

def get_current_price(symbol):
    try:
        return float(session.get_tickers(category="linear", symbol=symbol)["result"]["list"][0]["lastPrice"])
    except: return None

def place_short_market(symbol, qty):
    return session.place_order(category="linear", symbol=symbol, side="Sell", orderType="Market", qty=str(round(qty, 6)))

def get_position(symbol):
    pos = session.get_positions(category="linear", symbol=symbol)["result"]["list"]
    return pos[0] if pos else None

def close_position(symbol):
    pos = get_position(symbol)
    if pos and float(pos["size"]) > 0:
        session.place_order(category="linear", symbol=symbol, side="Buy", orderType="Market", qty=pos["size"], reduceOnly=True)
