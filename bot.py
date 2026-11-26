import requests
import time
import os
from datetime import datetime
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot attivo")
    def log_message(self, *a): pass
def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
Thread(target=keep_alive, daemon=True).start()
ODDS_KEY = os.getenv("ODDS_API_KEY")
FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAPPA = {135: "soccer_italy_serie_a", 136: "soccer_italy_serie_b", 39: "soccer_epl", 140: "soccer_spain_la_liga", 78: "soccer_germany_bundesliga", 61: "soccer_france_ligue_1", 2: "soccer_uefa_champs_league", 3: "soccer_uefa_europa_league", 71: "soccer_brazil_campeonato", 88: "soccer_netherlands_eredivisie", 848: "soccer_uefa_europa_conference_league",  94: "soccer_portugal_primeira_liga"}
def get_live_sports():
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers={"x-apisports-key": FOOTBALL_KEY}, timeout=15)
        data = r.json().get("response", [])
        leagues = set()
        for m in data:
            lid = m["league"]["id"]
            if lid in MAPPA: leagues.add(MAPPA[lid])
        print(f"Live ora: {len(data)} partite -> {list(leagues)}", flush=True)
        return list(leagues)
    except Exception as e:
        print(f"Errore live: {e}", flush=True)
        return ["soccer_italy_serie_a"]
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
def check_sport(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {"apiKey": ODDS_KEY, "regions": "eu", "markets": "totals", "oddsFormat": "decimal"}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200: return
    for match in r.json():
        for book in match.get("bookmakers", []):
            for market in book.get("markets", []):
                if market["key"] == "totals":
                    for out in market.get("outcomes", []):
                        if out["name"] == "Over" and out["point"] == 1.5 and out["price"] >= 1.40:
                            msg = f"⚽ <b>{match['home_team']} vs {match['away_team']}</b>\nOver 1.5 @ {out['price']} - {book['title']}"
                            send_telegram(msg)
print("BOT PARTITO - modalita live dinamica", flush=True)
while True:
    ora = datetime.now()
    print(f"Check ore {ora}", flush=True)
    if 11 <= ora.hour <= 23:
        for s in get_live_sports(): check_sport(s)
    else: print("Notte, pausa", flush=True)
    time.sleep(900)
