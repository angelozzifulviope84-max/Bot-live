import requests
import time
import os
from datetime import datetime
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot attivo")
    def log_message(self, *a):
        pass
def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
Thread(target=keep_alive, daemon=True).start()
FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
ODDS_KEY = os.getenv("ODDS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAPPA = {135: "soccer_italy_serie_a", 136: "soccer_italy_serie_b", 39: "soccer_epl", 140: "soccer_spain_la_liga", 78: "soccer_germany_bundesliga", 61: "soccer_france_ligue_1", 2: "soccer_uefa_champs_league", 3: "soccer_uefa_europa_league", 71: "soccer_brazil_campeonato", 88: "soccer_netherlands_eredivisie", 94: "soccer_portugal_primeira_liga", 848: "soccer_uefa_europa_conference_league"}
GIA_MANDATI = set()
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
def get_over15(sport, home, away):
    try:
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
        params = {"apiKey": ODDS_KEY, "regions": "eu", "markets": "totals", "oddsFormat": "decimal"}
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return 0
        for match in r.json():
            if home in match['home_team'] or away in match['away_team']:
                for book in match.get("bookmakers", []):
                    for market in book.get("markets", []):
                        if market["key"] == "totals":
                            for out in market.get("outcomes", []):
                                if out["name"] == "Over" and out["point"] == 1.5:
                                    return out["price"]
        return 0
    except:
        return 0
print("BOT PARTITO - PALETTI LIBRO ATTIVI", flush=True)
while True:
    try:
        ora = datetime.now()
        print(f"Check ore {ora}", flush=True)
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers={"x-apisports-key": FOOTBALL_KEY}, timeout=15)
        for m in r.json().get("response", []):
            lid = m["league"]["id"]
            if lid not in MAPPA:
                continue
            minuto = m["fixture"]["status"]["elapsed"]
            if minuto is None:
                continue
            casa = m["teams"]["home"]["name"]
            osp = m["teams"]["away"]["name"]
            gol_c = m["goals"]["home"]
            gol_o = m["goals"]["away"]
            nome = f"{casa} vs {osp}"
            fid = m["fixture"]["id"]
            over15 = get_over15(MAPPA[lid], casa, osp)
            if 14 <= minuto <= 16 and gol_c == 0 and gol_o == 0 and (fid, "1BALL_15") not in GIA_MANDATI:
                if over15 >= 1.40:
                    GIA_MANDATI.add((fid, "1BALL_15"))
                    send_telegram(f"1 BALL LAG 15' 1T\n<b>{nome}</b>\n0-0 al {minuto}' - Over 1.5 @ {over15}\nCHECK: 1 palla ancora li? Se si, controlla 0.75 e HDP -0.25 a 0.50-0.60")
            if 20 <= minuto <= 25 and gol_c == 0 and gol_o == 0 and (fid, "25MARK") not in GIA_MANDATI:
                if over15 >= 1.40:
                    GIA_MANDATI.add((fid, "25MARK"))
                    send_telegram(f"25TH MINUTE MARK\n<b>{nome}</b>\n0-0 al {minuto}' - Over 1.5 @ {over15}\nCHECK: O/U 0.75 paga 0.60-0.75? Se a 25' resta 0.75 a 0.70 / -1.00 = GOL IN ARRIVO. Se 0.50 paga 0.60-0.80 = ancora possibile. Se 0.50 paga 0.90+ = NO BET. + HDP -0.25 a 0.50-0.60?")
            if minuto == 45 and gol_c == 0 and gol_o == 0 and (fid, "PALLA_HT") not in GIA_MANDATI:
                GIA_MANDATI.add((fid, "PALLA_HT"))
                send_telegram(f"CHERRY PICK - PALLA HT 0-0\n<b>{nome}</b>\nFine 1T 0-0\nCHECK 2T: O/U 1 palla per 2T? Pareggio 1X2 sopra 2.00? Diff. 1X2 sopra 2.5? H2H da Over 2.5?")
            if 59 <= minuto <= 61 and gol_c == 0 and gol_o == 0 and (fid, "1BALL_60") not in GIA_MANDATI:
                GIA_MANDATI.add((fid, "1BALL_60"))
                send_telegram(f"1 BALL LAG 15' 2T - 60'\n<b>{nome}</b>\n0-0 al {minuto}'\nCHECK: 2 palle ancora li a 0.74? HDP -0.25? Stesso principio del 1T")
            if 59 <= minuto <= 61 and ((gol_c == 1 and gol_o == 0) or (gol_c == 0 and gol_o == 1)) and (fid, "2PALLE_10") not in GIA_MANDATI:
                GIA_MANDATI.add((fid, "2PALLE_10"))
                send_telegram(f"SUL 1-0: 2 PALLE\n<b>{nome}</b>\n{gol_c}-{gol_o} al {minuto}'\nCHECK: O/U 2 palle per il resto? HDP?")
    except Exception as e:
        print(f"Errore: {e}", flush=True)
    time.sleep(300)
