# Bybit Safe Pump Short Bot - Versione 500€ (Conservativa)

Strategia avanzata per shortare pump improvvisi di memecoin e altcoin su Bybit.
- Capitale: 500 USDT
- Rischio massimo per trade: ~1%
- Max 4 DCA (moltiplicatore 1.6x)
- Hard Stop Loss: -12% dal prezzo medio
- Target: +8.5%
- Solo 1 trade attivo alla volta

## Come partire
1. `python3 -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` → inserisci le tue chiavi Bybit
4. `python backtester.py` (backtest 6 mesi)
5. `python main.py` (usa prima TESTNET=true!)

Hosting: perfetto su AWS EC2 (tmux o systemd).
