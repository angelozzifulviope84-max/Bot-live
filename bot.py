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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAPPA = {135: "soccer_italy_serie_a", 136: "soccer_italy_serie_b", 39: "soccer_epl", 140: "soccer_spain_la_liga", 78: "soccer_germany_bundesliga", 61: "soccer_france_ligue_1", 2: "soccer_uefa_champs_league", 3: "soccer_uefa_europa_league", 71: "soccer_brazil_campeonato", 88: "soccer_netherlands_eredivisie", 94: "soccer_portugal_primeira_liga", 307: "soccer_saudi_pro_league", 848: "soccer_uefa_europa_conference_league"}
GIA_MANDATI = set()
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
def metodo_1ball_lag_15(nome, minuto, fid):
    if (fid, "1BALL_15") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "1BALL_15"))
    send_telegram(f"1 BALL LAG - 15' 1T\n<b>{nome}</b>\n0-0 al {minuto}'\nSe ancora a 1 palla, partita molto offensiva. Controlla 1 palla, poi 0.75 e 0.50")
def metodo_25th_minute_mark(nome, minuto, fid):
    if (fid, "25MARK") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "25MARK"))
    send_telegram(f"25TH MINUTE MARK\n<b>{nome}</b>\n0-0 al {minuto}'\nO/U 0.75 paga 0.60-0.75 = offensiva. Se a 25' resta 0.75 a 0.70 / -1.00 = gol in arrivo. Se 0.50 paga 0.60-0.80 = possibile. Se 0.50 paga 0.90+ = NO BET")
def metodo_cherry_pick_ht(nome, fid):
    if (fid, "PALLA_HT") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "PALLA_HT"))
    send_telegram(f"CHERRY PICK - PALLA HT 0-0\n<b>{nome}</b>\nFine 1T 0-0\nO/U 1 palla per 2T? Pareggio 1X2 sopra 2.00? Diff. 1X2 sopra 2.5? H2H da Over 2.5?")
def metodo_1ball_lag_60(nome, minuto, fid):
    if (fid, "1BALL_60") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "1BALL_60"))
    send_telegram(f"1 BALL LAG - 15' 2T 60'\n<b>{nome}</b>\n0-0 al {minuto}'\nSe ancora a 2 palle a 0.74, stessa cosa del 1T. Controlla HDP -0.25")
def metodo_sul_1a0_2palle(nome, minuto, gol_c, gol_o, fid):
    if (fid, "2PALLE_10") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "2PALLE_10"))
    send_telegram(f"SUL 1-0: 2 PALLE\n<b>{nome}</b>\n{gol_c}-{gol_o} al {minuto}'\nControlla O/U 2 palle")
def metodo_hdp_025(nome, minuto, fid):
    if (fid, "HDP025") in GIA_MANDATI:
        return
    GIA_MANDATI.add((fid, "HDP025"))
    send_telegram(f"0.25 HDP MAGIC\n<b>{nome}</b>\n0-0 al {minuto}'\nFavorita -0.25 a 0.50-0.60 = sta dominando")
print("BOT PARTITO - SOLO LIBRO", flush=True)
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
            if 14 <= minuto <= 16 and gol_c == 0 and gol_o == 0:
                metodo_1ball_lag_15(nome, minuto, fid)
                metodo_hdp_025(nome, minuto, fid)
            if 20 <= minuto <= 25 and gol_c == 0 and gol_o == 0:
                metodo_25th_minute_mark(nome, minuto, fid)
            if minuto == 45 and gol_c == 0 and gol_o == 0:
                metodo_cherry_pick_ht(nome, fid)
            if 59 <= minuto <= 61 and gol_c == 0 and gol_o == 0:
                metodo_1ball_lag_60(nome, minuto, fid)
            if 59 <= minuto <= 61 and ((gol_c == 1 and gol_o == 0) or (gol_c == 0 and gol_o == 1)):
                metodo_sul_1a0_2palle(nome, minuto, gol_c, gol_o, fid)
    except Exception as e:
        print(f"Errore: {e}", flush=True)
    time.sleep(300)
