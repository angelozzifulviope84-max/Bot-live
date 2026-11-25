import requests
import time
from datetime import datetime, timezone
import os
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

TELEGRAM_TOKEN = "9273636150:AAG-WbSYB80zWzEpw9iD1coUAPyi7HSAQZQ"
CHAT_ID = "5803856763"
ODDS_API_KEY = "38e7754bcff7f4082b8a54033b1c0cea"

def manda(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo})

manda("✅ Bot su RENDER acceso! Sempre attivo 24/24")

SPORTS = ["soccer_italy_serie_a", "soccer_italy_serie_b", "soccer_italy_serie_a_women", "soccer_epl", "soccer_england_championship", "soccer_england_league1", "soccer_england_womens_super_league", "soccer_spain_la_liga", "soccer_spain_segunda_division", "soccer_spain_primera_division_women", "soccer_germany_bundesliga", "soccer_germany_bundesliga2", "soccer_germany_frauen_bundesliga", "soccer_france_ligue_1", "soccer_france_ligue_2", "soccer_france_division_1_feminine", "soccer_uefa_champs_league", "soccer_uefa_europa_league", "soccer_uefa_europa_conference_league", "soccer_uefa_nations_league", "soccer_uefa_womens_champs_league", "soccer_portugal_primeira_liga", "soccer_netherlands_eredivisie", "soccer_netherlands_eredivisie_women", "soccer_belgium_first_div", "soccer_scotland_premiership", "soccer_turkey_super_league", "soccer_greece_super_league", "soccer_switzerland_superleague", "soccer_austria_bundesliga", "soccer_denmark_superliga", "soccer_denmark_kvindeliga", "soccer_sweden_allsvenskan", "soccer_sweden_damallsvenskan", "soccer_norway_eliteserien", "soccer_norway_toppserien", "soccer_finland_veikkausliiga", "soccer_poland_ekstraklasa", "soccer_czech_republic_czech_liga", "soccer_croatia_hnl", "soccer_serbia_superliga", "soccer_romania_liga_i", "soccer_bulgaria_first_league", "soccer_hungary_nb_i", "soccer_brazil_serie_a", "soccer_brazil_serie_b", "soccer_argentina_primera_division", "soccer_chile_primera_division", "soccer_colombia_primera_a", "soccer_peru_primera_division", "soccer_usa_mls", "soccer_usa_nwsl", "soccer_mexico_ligamx", "soccer_japan_j_league", "soccer_korea_kleague1", "soccer_china_superleague", "soccer_australia_aleague", "soccer_australia_a_league_women", "soccer_india_super_league", "soccer_indonesia_liga_1", "soccer_thailand_thai_league_1", "soccer_vietnam_v_league_1", "soccer_singapore_premier_league", "soccer_malaysia_super_league", "soccer_saudi_arabia_professional_league", "soccer_uae_pro_league", "soccer_qatar_stars_league", "soccer_egypt_premier_league", "soccer_south_africa_premier_league", "soccer_morocco_botola_pro", "soccer_israel_premier_league", "soccer_iceland_urvalsdeild", "soccer_ireland_premier_division", "soccer_wales_premier_league", "soccer_northern_ireland_premiership", "soccer_cyprus_first_division", "soccer_slovenia_prva_liga", "soccer_bosnia_premier_league", "soccer_albania_superliga", "soccer_conmebol_copa_libertadores", "soccer_conmebol_copa_sudamericana"]
gia = set()

while True:
    try:
        ora = datetime.now(timezone.utc)
        for sport in SPORTS:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals,spreads&oddsFormat=decimal"
            data = requests.get(url).json()
            if not isinstance(data, list):
                continue
            for match in data:
                try:
                    inizio = datetime.fromisoformat(match.get("commence_time","").replace("Z", "+00:00"))
                except:
                    continue
                minuti = (ora - inizio).total_seconds() / 60
                if minuti < 0 or minuti > 95:
                    continue
                nome = f"{match.get('home_team','')} vs {match.get('away_team','')}"
                for book in match.get("bookmakers", []):
                    for m in book.get("markets", []):
                        if m.get("key") == "totals":
                            for o in m.get("outcomes", []):
                                if o.get("name") == "Over" and o.get("point") == 0.5:
                                    q = o.get("price", 0)
                                    chiave = nome + "_over05"
                                    if 0.60 <= q <= 0.85 and 20 <= minuti <= 35 and chiave not in gia:
                                        manda(f"🔥 LIVE {int(minuti)}' - OVER 0.5 1T\n\n⚽ {nome}\n💰 @{q}")
                                        gia.add(chiave)
                                if o.get("name") == "Over" and o.get("point") == 1.5:
                                    q = o.get("price", 0)
                                    chiave = nome + "_forever"
                                    if 1.60 <= q <= 2.10 and 60 <= minuti <= 80 and chiave not in gia:
                                        manda(f"♾️ LIVE {int(minuti)}' - FOREVER 1 BALL\n\n⚽ {nome}\n💰 @{q}")
                                        gia.add(chiave)
                        if m.get("key") == "spreads":
                            for o in m.get("outcomes", []):
                                if o.get("point") == -0.25:
                                    q = o.get("price", 0)
                                    chiave = nome + "_magia_" + str(o.get("name"))
                                    if 1.80 <= q <= 2.20 and 55 <= minuti <= 75 and chiave not in gia:
                                        manda(f"✨ LIVE {int(minuti)}' - MAGIA -0.25\n\n⚽ {nome}\n👉 {o.get('name')}\n💰 @{q}")
                                        gia.add(chiave)
        time.sleep(300)
    except Exception as e:
        print("Errore:", e)
        time.sleep(60)
