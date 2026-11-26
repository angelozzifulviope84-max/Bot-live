import requests
import os
import time
import threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot attivo", 200

@app.route("/ping")
def ping():
    return "pong", 200

def keep_alive():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()

FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAPPA = {
    135: "soccer_italy_serie_a",
    136: "soccer_italy_serie_b",
    137: "soccer_italy_serie_c",
    138: "soccer_italy_coppa_italia",
    2: "soccer_uefa_champs_league",
    3: "soccer_uefa_europa_league",
    848: "soccer_uefa_europa_conference_league",
    39: "soccer_england_premier_league",
    40: "soccer_england_championship",
    41: "soccer_england_league_1",
    42: "soccer_england_league_2",
    45: "soccer_england_fa_cup",
    48: "soccer_england_league_cup",
    140: "soccer_spain_la_liga",
    141: "soccer_spain_segunda",
    143: "soccer_spain_copa_del_rey",
    78: "soccer_germany_bundesliga",
    79: "soccer_germany_bundesliga_2",
    80: "soccer_germany_3_liga",
    81: "soccer_germany_dfb_pokal",
    61: "soccer_france_ligue_1",
    62: "soccer_france_ligue_2",
    66: "soccer_france_coupe_de_france",
    94: "soccer_portugal_primeira",
    95: "soccer_portugal_segunda",
    88: "soccer_netherlands_eredivisie",
    89: "soccer_netherlands_eerste",
    144: "soccer_belgium_first_div_a",
    179: "soccer_scotland_premiership",
    203: "soccer_turkey_super_lig",
    197: "soccer_greece_super_league",
    207: "soccer_switzerland_super_league",
    218: "soccer_austria_bundesliga",
    119: "soccer_denmark_superliga",
    113: "soccer_sweden_allsvenskan",
    103: "soccer_norway_eliteserien",
    106: "soccer_poland_ekstraklasa",
    162: "soccer_czech_first_league",
    171: "soccer_croatia_hnl",
    286: "soccer_serbia_super_liga",
    283: "soccer_romania_liga_1",
    227: "soccer_ukraine_premier_league",
    235: "soccer_russia_premier_league",
    71: "soccer_brazil_serie_a",
    72: "soccer_brazil_serie_b",
    128: "soccer_argentina_primera",
    13: "soccer_conmebol_libertadores",
    11: "soccer_conmebol_sudamericana",
    253: "soccer_usa_mls",
    262: "soccer_mexico_liga_mx",
    98: "soccer_japan_j1_league",
    292: "soccer_korea_k_league_1",
}

GIA_MANDATI = set()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Errore telegram: {e}", flush=True)

def metodo_1ball_lag_15(casa, osp):
    key = f"{casa}-{osp}-1ball15"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"⚽🔥 1 BALL LAG 15'\n\n{casa} - {osp}\n📊 Over 1.5\n💰 Quota min: 1.40")

def metodo_25th(casa, osp):
    key = f"{casa}-{osp}-25th"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"⚽🔥 25TH MINUTE MARK\n\n{casa} - {osp}\n📊 Over 1.5\n💰 Quota min: 1.40")

def metodo_cherry(casa, osp):
    key = f"{casa}-{osp}-cherry"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"🍒 CHERRY PICK - PALLA HT\n\n{casa} - {osp}\n📊 Over 0.5 HT")

def metodo_1ball60(casa, osp):
    key = f"{casa}-{osp}-1ball60"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"⚽🔥 1 BALL LAG 60'\n\n{casa} - {osp}\n📊 Over 1.5")

def metodo_1_0_2palle(casa, osp):
    key = f"{casa}-{osp}-1-0-2palle"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"⚽ SUL 1-0: 2 PALLE\n\n{casa} - {osp}\n📊 Over 2.5")

def metodo_hdp025(casa, osp):
    key = f"{casa}-{osp}-hdp025"
    if key in GIA_MANDATI:
        return
    GIA_MANDATI.add(key)
    send_telegram(f"⚽ HDP 0.25\n\n{casa} - {osp}")

while True:
    try:
        ora = datetime.now()
        print(f"Check ore {ora}", flush=True)
        r = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers={"x-apisports-key": FOOTBALL_API_KEY})
        lista = r.json().get("response", [])
        print(f"Totale live API: {len(lista)}", flush=True)
        filtrate = 0
        for m in lista:
            lid = m["league"]["id"]
            if lid not in MAPPA:
                continue
            filtrate += 1
            minuto = m["fixture"]["status"]["elapsed"]
            if minuto is None:
                continue
            casa = m["teams"]["home"]["name"]
            osp = m["teams"]["away"]["name"]
            gol_c = m["goals"]["home"]
            gol_o = m["goals"]["away"]
            print(f"{casa}-{osp} {gol_c}-{gol_o} min {minuto} lega {lid}", flush=True)
            if 13 <= minuto <= 17 and gol_c == 0 and gol_o == 0:
                metodo_1ball_lag_15(casa, osp)
            if 20 <= minuto <= 26 and gol_c == 0 and gol_o == 0:
                metodo_25th(casa, osp)
            if 44 <= minuto <= 46 and gol_c == 0 and gol_o == 0:
                metodo_cherry(casa, osp)
            if 58 <= minuto <= 63:
                metodo_1ball60(casa, osp)
            if gol_c == 1 and gol_o == 0:
                metodo_1_0_2palle(casa, osp)
            if gol_c == 0 and gol_o == 0:
                metodo_hdp025(casa, osp)
        print(f"Filtrate MAPPA: {filtrate} - Controllo finito", flush=True)
    except Exception as e:
        print(f"Errore check: {e}", flush=True)
    time.sleep(300)

keep_alive()
