import schedule
import time
from scanner import get_top_gainers
from position_manager import manage_trade
from config import CHECK_INTERVAL_MIN
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main_loop():
    print("🔄 Scan in corso...")
    gainers = get_top_gainers()
    for g in gainers:
        manage_trade(g["symbol"], g["price"])
        time.sleep(1.5)

schedule.every(CHECK_INTERVAL_MIN).minutes.do(main_loop)

print("🚀 Bot avviato - Modalità SAFE 500€ - TESTNET consigliata!")
while True:
    schedule.run_pending()
    time.sleep(60)
